FROM eclipse-temurin:21-jdk AS build
WORKDIR /app
COPY . .
RUN chmod +x ./gradlew
RUN ./gradlew installDist --no-daemon -x test

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/build/install/ /app/build/install/
ENV PORT=8080
EXPOSE 8080
CMD ["/app/build/install/holisto/bin/holisto"]
