docker-compose down
docker-compose up -d --build
docker ps


echo "=========================================="
echo "🌐 Airflow UI  : http://localhost:8080"
echo "📡 Kafka       : localhost:9092"
echo "⚡ Spark(local): docker internal local setup"
echo "=========================================="