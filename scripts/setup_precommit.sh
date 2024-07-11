#!/bin/bash
printf $"#/bin/sh\nblack ."> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit