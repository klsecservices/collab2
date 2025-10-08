conn = new Mongo();
db = conn.getDB("collab2");
db.domains.insertOne({"host": "test123123.localhost", "accesskey": "testaccesskey"})
db.responses.insertOne({"host": "test123123.localhost", "id":"123456", "pattern":".*", "responsebody": "", "responsecode": 200, "responseheaders": [{"key": "Content-Type", "value": "image/png"}, {"key": "Foo", "value": "bar"}], "priority": 2});