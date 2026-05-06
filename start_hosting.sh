#!
cd "."

echo "Launching hosting..."
ssh -R 80:127.0.0.1:5000 localhost.run