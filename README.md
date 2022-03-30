# To post local PC date and Time as json topic to a MQTT server.
# Create a binary and distribute along with mqtt.json
 ```pyinstaller -F timedata.py
 ```

# Create a windows service using (nssm)[https://nssm.cc/release/nssm-2.24.zip]

 ```
 nssm.exe install "ServiceName" .\dist\timedata.exe
 ```
