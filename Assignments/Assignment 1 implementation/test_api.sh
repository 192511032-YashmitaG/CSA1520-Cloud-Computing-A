#!/usr/bin/env bash
set -e
curl -i http://localhost:5000/health
curl -i http://localhost:5000/api/students
curl -i http://localhost:5000/api/students/1
curl -i http://localhost:5000/api/students/999 || true
