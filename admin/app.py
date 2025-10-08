from flask import Flask, request, jsonify
from pymongo import MongoClient # type: ignore
import hashlib
import base64
import os
from datetime import datetime, timezone
import re
import random
import string

rand_string = lambda n: ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

app = Flask(__name__)

client = MongoClient("mongodb://db:27017/")
db = client["collab2"]
requests_col = db["requests"]
dns_requests_col = db["dns_requests"]
smtp_requests_col = db["smtp_requests"]
responses_col = db["responses"]
domains_col = db["domains"]
dns_records_col = db["dns_records"]
base_domain = os.getenv("BASE_DOMAIN")

def get_value(data, key):
    value = data.get(key)
    if isinstance(value, str) or isinstance(value, int) or isinstance(value, bool):
        return value
    return None

def generate_access_key():
    return base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")

def get_domain_by_key(access_key):
    return domains_col.find_one({"accesskey": access_key})

@app.route("/api/createDomain", methods=["POST"])
def create_domain():
    data = request.json
    host = get_value(data, "host")
    if host == "" or host == None:
        host = rand_string(16)
    if not re.match(r"^[a-zA-Z0-9_-]+$", host) or host.startswith("_") or host == "www":
        return jsonify({"error": "invalid host"}), 400
    host = host.lower() + "." + base_domain
    if domains_col.find_one({"host": host}):
        return jsonify({"error": "domain already exists"}), 403
    access_key = generate_access_key()
    domains_col.insert_one({"host": host, "accesskey": access_key})
    return jsonify({"accessKey": access_key, "host": host})

@app.route("/api/getDomain", methods=["POST"])
def get_domain():
    data = request.json
    access_key = get_value(data, "accessKey")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    request_count_http = requests_col.count_documents({"host": domain["host"]})
    request_count_dns = dns_requests_col.count_documents({"host": domain["host"]})
    request_count_smtp = smtp_requests_col.count_documents({"host": domain["host"]})
    return jsonify({"host": domain["host"], "requestCountHttp": request_count_http, "requestCountDns": request_count_dns, "requestCountSmtp": request_count_smtp})

@app.route("/api/getRequests", methods=["POST"])
def get_requests():
    data = request.json
    access_key = get_value(data, "accessKey")
    after = get_value(data, "after")
    pattern_id = get_value(data, "patternId")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    query = {"host": domain["host"]}
    if after:
        try:
            after_datetime = datetime.fromtimestamp(int(after), timezone.utc)
            query["timestamp"] = {"$gt": after_datetime}
        except ValueError:
            return jsonify({"error": "invalid after parameter"}), 400
    if pattern_id:
        query["patternid"] = pattern_id
    requests = list(requests_col.find(query, {"_id": 0}))
    for req in requests:
        if isinstance(req.get("rawrequest"), bytes):
            req["rawrequest"] = base64.b64encode(req["rawrequest"]).decode("utf-8")
        if "timestamp" in req:
            req["timestamp"] = int(req["timestamp"].timestamp())
    return jsonify(requests)

@app.route("/api/getDNSRequests", methods=["POST"])
def get_dns_requests():
    data = request.json
    access_key = get_value(data, "accessKey")
    after = get_value(data, "after")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    
    if get_value(data, "patternId"):
        return jsonify([])
    
    query = {"host": domain["host"]}
    if after:
        try:
            after_datetime = datetime.fromtimestamp(int(after), timezone.utc)
            query["timestamp"] = {"$gt": after_datetime}
        except ValueError:
            return jsonify({"error": "invalid after parameter"}), 400

    requests = list(dns_requests_col.find(query, {"_id": 0}))
    for req in requests:
        if "timestamp" in req:
            req["timestamp"] = int(req["timestamp"].timestamp())
    return jsonify(requests)

@app.route("/api/getSMTPRequests", methods=["POST"])
def get_smtp_requests():
    data = request.json
    access_key = get_value(data, "accessKey")
    after = get_value(data, "after")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    
    if get_value(data, "patternId"):
        return jsonify([])
    
    query = {"host": domain["host"]}
    if after:
        try:
            after_datetime = datetime.fromtimestamp(int(after), timezone.utc)
            query["timestamp"] = {"$gt": after_datetime}
        except ValueError:
            return jsonify({"error": "invalid after parameter"}), 400

    requests = list(smtp_requests_col.find(query, {"_id": 0}))
    for req in requests:
        if "timestamp" in req:
            req["timestamp"] = int(req["timestamp"].timestamp())
        if isinstance(req.get("data"), bytes):
            req["data"] = base64.b64encode(req["data"]).decode("utf-8")
    return jsonify(requests)

@app.route("/api/getPatterns", methods=["POST"])
def get_patterns():
    data = request.json
    access_key = get_value(data, "accessKey")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    patterns = list(responses_col.find({"host": domain["host"]}, {"_id": 0}))
    return jsonify(patterns)

@app.route("/api/updatePattern", methods=["POST"])
def update_pattern():
    data = request.json
    access_key = get_value(data, "accessKey")
    
    response_data = data.get("response")
    if not response_data:
        return jsonify({"error": "invalid request"}), 400
    
    pattern_id = get_value(response_data, "id")
    if not pattern_id:
        return jsonify({"error": "invalid request"}), 400
    
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key or host mismatch"}), 403
    
    fields_to_update = ["pattern", "priority", "responsebody", "responsecode", "responseheaders", "externalHandler"]
    update_data = {field: get_value(response_data, field) for field in fields_to_update if field in response_data}
    unset_data = {field: 1 for field in fields_to_update if field not in response_data}
    update_result = responses_col.update_one({"id": pattern_id, "host": domain["host"]}, {"$set": update_data, "$unset": unset_data})
    return jsonify({"success": update_result.modified_count > 0})

@app.route("/api/createPattern", methods=["POST"])
def create_pattern():
    data = request.json
    access_key = get_value(data, "accessKey")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    pattern_id = hashlib.sha256(os.urandom(16)).hexdigest()
    new_pattern = {
        "host": domain["host"],
        "id": pattern_id,
        "pattern": ".*",
        "priority": 0,
        "responsebody": "",
        "responsecode": 200,
        "responseheaders": [{"key": "Content-Type", "value": "text/html"}]
    }
    responses_col.insert_one(new_pattern)
    del new_pattern["_id"]
    return jsonify(new_pattern)

@app.route("/api/deletePattern", methods=["POST"])
def delete_pattern():
    data = request.json
    access_key = get_value(data, "accessKey")
    pattern_id = get_value(data, "id")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    delete_result = responses_col.delete_one({"id": pattern_id, "host": domain["host"]})
    return jsonify({"success": delete_result.deleted_count > 0})

@app.route("/api/getDnsRecords", methods=["POST"])
def get_dns_records():
    data = request.json
    access_key = get_value(data, "accessKey")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    records = list(dns_records_col.find({"host": domain["host"]}, {"_id": 0}))
    return jsonify(records)

@app.route("/api/createDnsRecord", methods=["POST"])
def create_dns_record():
    data = request.json
    access_key = get_value(data, "accessKey")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    record = {
        "host": domain["host"],
        "responsetype": "static",
        "id": hashlib.sha256(os.urandom(16)).hexdigest(),
        "name": "@",
        "value": "",
        "ttl": "3600",
        "type": "TXT"
    }
    dns_records_col.insert_one(record)
    del record["_id"]
    return jsonify(record)

@app.route("/api/updateDnsRecord", methods=["POST"])
def update_dns_record():
    data = request.json
    access_key = get_value(data, "accessKey")
    
    record = data.get("record")
    if not record:
        return jsonify({"error": "invalid request"}), 400
    
    record_id = get_value(record, "id")
    if not record_id:
        return jsonify({"error": "invalid request"}), 400
    
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    
    if "responsetype" not in record:
        record["responsetype"] = "static"
    
    if record["responsetype"] == "static":
        fields_to_update = ["name", "value", "ttl", "type", "responsetype"]
    elif record["responsetype"] == "rebind":
        fields_to_update = ["name", "value1", "value2", "type", "responsetype"]
    else:
        return jsonify({"error": "invalid request"}), 400

    update_data = {field: get_value(record, field) for field in fields_to_update if field in record}
    unset_data = {field: 1 for field in fields_to_update if field not in record}
    update_result = dns_records_col.update_one({"id": record_id, "host": domain["host"]}, {"$set": update_data, "$unset": unset_data})
    return jsonify({"success": update_result.modified_count > 0})

@app.route("/api/deleteDnsRecord", methods=["POST"])
def delete_dns_record():
    data = request.json
    access_key = get_value(data, "accessKey")
    record_id = get_value(data, "id")
    domain = get_domain_by_key(access_key)
    if not domain:
        return jsonify({"error": "invalid access key"}), 403
    delete_result = dns_records_col.delete_one({"id": record_id, "host": domain["host"]})
    return jsonify({"success": delete_result.deleted_count > 0})

if __name__ == "__main__":
    app.run(debug=False)