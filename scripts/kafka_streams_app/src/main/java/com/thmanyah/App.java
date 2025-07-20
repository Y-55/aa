package com.thmanyah;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.Deserializer;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serializer;
import org.apache.kafka.connect.json.JsonDeserializer;
import org.apache.kafka.connect.json.JsonSerializer;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.util.Properties;

public class App {
    
    private static final Logger logger = LoggerFactory.getLogger(App.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    // Topic names
    private static final String ENGAGEMENT_EVENTS_TOPIC = "pg.public.engagement_events";
    private static final String CONTENT_TOPIC = "pg.public.content";
    private static final String OUTPUT_TOPIC = "ks.content_engagement_transformed";
    
    public static void main(String[] args) {
        Properties props = createStreamProperties();
        
        StreamsBuilder builder = new StreamsBuilder();
        buildTopology(builder);
        
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        
        // Add shutdown hook for graceful termination
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
        
        logger.info("Starting Engagement Enrichment Kafka Streams Application...");
        streams.start();
    }
    
    private static Properties createStreamProperties() {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "engagement-enrichment-app");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "redpanda-1:29092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, JsonSerde.class);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        
        // Enable caching and batching for better performance
        props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 10 * 1024 * 1024L);
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);
        
        return props;
    }
    
    private static void buildTopology(StreamsBuilder builder) {
        // Create JSON Serde
        Serde<JsonNode> jsonSerde = new JsonSerde();
        
        // Read engagement events stream
        KStream<String, JsonNode> engagementEvents = builder
            .stream(ENGAGEMENT_EVENTS_TOPIC, Consumed.with(Serdes.String(), jsonSerde))
            .peek((key, value) -> logger.debug("Processing engagement event: {}", value));
        
        // Read content stream and create a table for lookups
        KTable<String, JsonNode> contentTable = builder
            .stream(CONTENT_TOPIC, Consumed.with(Serdes.String(), jsonSerde))
            .peek((key, value) -> logger.debug("Processing content: {}", value))
            .toTable(Named.as("content-table"));
        
        // Extract content_id from engagement events for joining
        KStream<String, JsonNode> engagementWithContentKey = engagementEvents
            .selectKey((key, value) -> extractContentId(value))
            .filter((contentId, value) -> contentId != null);
        
        // Join engagement events with content data
        KStream<String, JsonNode> enrichedEvents = engagementWithContentKey
            .leftJoin(contentTable, App::enrichEngagementEvent,
                     Joined.with(Serdes.String(), jsonSerde, jsonSerde))
            .filter((key, value) -> value != null);
        
        // Send enriched events to output topic
        enrichedEvents
            .peek((key, value) -> logger.info("Enriched event: {}", value))
            .to(OUTPUT_TOPIC, Produced.with(Serdes.String(), jsonSerde));
    }
    
    /**
     * Extract content_id from engagement event for joining
     */
    private static String extractContentId(JsonNode engagementEvent) {
        try {
            // Handle Debezium CDC format - check if data is in 'after' field
            JsonNode afterNode = engagementEvent.get("after");
            if (afterNode != null && !afterNode.isNull()) {
                JsonNode contentIdNode = afterNode.get("content_id");
                if (contentIdNode != null && !contentIdNode.isNull()) {
                    return contentIdNode.asText();
                }
                
                // Alternative field names in case the schema varies
                contentIdNode = afterNode.get("contentId");
                if (contentIdNode != null && !contentIdNode.isNull()) {
                    return contentIdNode.asText();
                }
            }
            
            // Fallback: try root level (for non-CDC format)
            JsonNode contentIdNode = engagementEvent.get("content_id");
            if (contentIdNode != null && !contentIdNode.isNull()) {
                return contentIdNode.asText();
            }
            
            // Alternative field names in case the schema varies
            contentIdNode = engagementEvent.get("contentId");
            if (contentIdNode != null && !contentIdNode.isNull()) {
                return contentIdNode.asText();
            }
            
            logger.warn("No content_id found in engagement event: {}", engagementEvent);
            return null;
        } catch (Exception e) {
            logger.error("Error extracting content_id from event: {}", engagementEvent, e);
            return null;
        }
    }
    
    /**
     * Enrich engagement event with content data and perform transformations
     */
    private static JsonNode enrichEngagementEvent(JsonNode engagementEvent, JsonNode contentData) {
        try {
            // Handle Debezium CDC format - extract the actual event data from 'after' field
            JsonNode eventData = engagementEvent;
            JsonNode afterNode = engagementEvent.get("after");
            if (afterNode != null && !afterNode.isNull()) {
                eventData = afterNode;
            }
            
            ObjectNode enrichedEvent = eventData.deepCopy();
            
            // Add content data if available
            if (contentData != null) {
                // Handle content data that might also be in CDC format
                JsonNode contentAfterNode = contentData.get("after");
                JsonNode actualContentData = (contentAfterNode != null && !contentAfterNode.isNull()) ? contentAfterNode : contentData;
                
                // Add content_type
                JsonNode contentTypeNode = actualContentData.get("content_type");
                if (contentTypeNode != null && !contentTypeNode.isNull()) {
                    enrichedEvent.set("content_type", contentTypeNode);
                } else {
                    enrichedEvent.putNull("content_type");
                }
                
                // Add length_seconds
                JsonNode lengthSecondsNode = actualContentData.get("length_seconds");
                if (lengthSecondsNode != null && !lengthSecondsNode.isNull()) {
                    enrichedEvent.set("length_seconds", lengthSecondsNode);
                } else {
                    enrichedEvent.putNull("length_seconds");
                }
                
                // Calculate derived fields
                calculateDerivedFields(enrichedEvent, lengthSecondsNode);
            } else {
                // No content data found
                enrichedEvent.putNull("content_type");
                enrichedEvent.putNull("length_seconds");
                calculateDerivedFields(enrichedEvent, null);
            }
            
            return enrichedEvent;
            
        } catch (Exception e) {
            logger.error("Error enriching engagement event: {}", engagementEvent, e);
            return null;
        }
    }
    
    /**
     * Calculate engagement_seconds and engagement_pct
     */
    private static void calculateDerivedFields(ObjectNode enrichedEvent, JsonNode lengthSecondsNode) {
        try {
            // Calculate engagement_seconds from duration_ms
            JsonNode durationMsNode = enrichedEvent.get("duration_ms");
            if (durationMsNode != null && !durationMsNode.isNull() && durationMsNode.isNumber()) {
                double durationMs = durationMsNode.asDouble();
                double engagementSeconds = durationMs / 1000.0;
                enrichedEvent.put("engagement_seconds", engagementSeconds);
                
                // Calculate engagement_pct
                if (lengthSecondsNode != null && !lengthSecondsNode.isNull() && 
                    lengthSecondsNode.isNumber() && lengthSecondsNode.asDouble() > 0) {
                    
                    double lengthSeconds = lengthSecondsNode.asDouble();
                    double engagementPct = (engagementSeconds / lengthSeconds) * 100.0;
                    
                    // Round to 2 decimal places
                    BigDecimal rounded = BigDecimal.valueOf(engagementPct)
                        .setScale(2, RoundingMode.HALF_UP);
                    
                    enrichedEvent.put("engagement_pct", rounded.doubleValue());
                } else {
                    enrichedEvent.putNull("engagement_pct");
                }
            } else {
                // No duration_ms available
                enrichedEvent.putNull("engagement_seconds");
                enrichedEvent.putNull("engagement_pct");
            }
            
        } catch (Exception e) {
            logger.error("Error calculating derived fields", e);
            enrichedEvent.putNull("engagement_seconds");
            enrichedEvent.putNull("engagement_pct");
        }
    }
    
    /**
     * Custom JSON Serde for JsonNode
     */
    public static class JsonSerde implements Serde<JsonNode> {
        private final JsonSerializer jsonSerializer = new JsonSerializer();
        private final JsonDeserializer jsonDeserializer = new JsonDeserializer();
        
        @Override
        public Serializer<JsonNode> serializer() {
            return jsonSerializer;
        }
        
        @Override
        public Deserializer<JsonNode> deserializer() {
            return jsonDeserializer;
        }
    }
}