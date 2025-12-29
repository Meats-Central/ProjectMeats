#!/bin/bash
# Test if arguments would work

STATUS="failure"
ENVIRONMENT="dev"
COMPONENT="frontend"
COMMIT_SHA="abc123"
ERROR_MESSAGE="Frontend deployment or health check failed"

echo "STATUS='$STATUS'"
echo "ENVIRONMENT='$ENVIRONMENT'"
echo "COMPONENT='$COMPONENT'"
echo "COMMIT_SHA='$COMMIT_SHA'"
echo "ERROR_MESSAGE='$ERROR_MESSAGE'"

if [ -z "$STATUS" ] || [ -z "$ENVIRONMENT" ] || [ -z "$COMPONENT" ]; then
  echo "FAIL: Missing required arguments"
  exit 1
else
  echo "PASS: All arguments present"
  exit 0
fi
