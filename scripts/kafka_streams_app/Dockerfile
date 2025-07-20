FROM maven:amazoncorretto AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM openjdk:17-jdk-slim
WORKDIR /app
COPY --from=build /app/target/kafka_streams_app-1.0-SNAPSHOT.jar app.jar
COPY --from=build /app/target/lib/ lib/
CMD ["java", "-cp", "app.jar:lib/*", "com.thmanyah.App"]
