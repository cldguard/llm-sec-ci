#!/usr/bin/env python3
import os, json, uuid, time, boto3
from pathlib import Path
REGION = os.getenv("AWS_REGION","us-east-1")
def asff(scanner, summary, account_id):
    sev="LOW"
    if scanner in ["promptfoo-dvla","promptfoo-recruit"] and summary.get("failed",0): sev="MEDIUM"
    if scanner.startswith("garak") and summary.get("issues",0): sev="HIGH"
    if scanner=="trivy":
        if summary.get("critical",0)>0: sev="HIGH"
        elif summary.get("high",0)>0: sev="MEDIUM"
    return {"SchemaVersion":"2018-10-08","Id":str(uuid.uuid4()),
      "ProductArn":f"arn:aws:securityhub:{REGION}::product/{account_id}/default",
      "GeneratorId":f"{scanner}-ci","AwsAccountId":account_id,
      "Types":["Software and Configuration Checks/LLM Security"],
      "CreatedAt":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
      "UpdatedAt":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
      "Severity":{"Label":sev},
      "Title":f"{scanner.upper()} scan summary",
      "Description":json.dumps(summary),
      "Resources":[{"Type":"Other","Id":f"llm-sec::{scanner}","Region":REGION}]}
def main():
    client=boto3.client("securityhub",region_name=REGION)
    acct=os.getenv("AWS_ACCOUNT_ID","000000000000")
    findings=[]
    for name in ["promptfoo-dvla","promptfoo-recruit","garak-dvla","garak-recruit","art","trivy"]:
        p=Path(f"artifacts/normalized/{name}.json")
        if p.exists():
            data=json.loads(p.read_text())
            findings.append(asff(name,data.get("summary",{}),acct))
    if findings:
        print(client.batch_import_findings(Findings=findings))
    else:
        print("No findings to import")
if __name__=="__main__": main()