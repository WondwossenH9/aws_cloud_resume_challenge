# AWS Cloud Resume Challenge - Complete Deployment Guide

This guide will walk you through deploying your Cloud Resume Challenge step by step.

## Prerequisites

Before starting, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **AWS SAM CLI** installed
4. **Git** installed
5. **Python 3.9+** installed
6. **Node.js 18+** installed (for frontend validation)
7. **Domain name** (optional, for custom domain)

## Step-by-Step Deployment

### 1. AWS Certification
- **What**: Get AWS Cloud Practitioner certification
- **Why**: Demonstrates foundational AWS knowledge
- **How**: Study and pass the CLF-C02 exam
- **Cost**: $100 USD
- **Resources**: [ExamPro AWS Cloud Practitioner Course](https://exampro.co/aws-cloud-practitioner)

### 2. Set Up AWS CLI and SAM CLI

```bash
# Install AWS CLI (if not already installed)
# Windows: Download from AWS website
# macOS: brew install awscli
# Linux: sudo apt-get install awscli

# Configure AWS CLI
aws configure
# Enter your Access Key ID, Secret Access Key, region (us-east-1), and output format (json)

# Install AWS SAM CLI
# Windows: Download from AWS website
# macOS: brew install aws-sam-cli
# Linux: Follow AWS documentation
```

### 3. Create GitHub Repository

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: Cloud Resume Challenge setup"

# Create repository on GitHub and push
git remote add origin https://github.com/yourusername/aws-cloud-resume-challenge.git
git branch -M main
git push -u origin main
```

### 4. Set Up GitHub Secrets

In your GitHub repository, go to Settings > Secrets and variables > Actions, and add:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `API_GATEWAY_URL`: Will be set after backend deployment
- `CLOUDFRONT_DISTRIBUTION_ID`: Will be set after CloudFront setup

### 5. Deploy Backend Infrastructure

```bash
# Navigate to infrastructure directory
cd infrastructure

# Build the SAM application
sam build --template template.yaml

# Deploy the application
sam deploy --guided
# Follow the prompts:
# - Stack Name: cloud-resume-challenge-backend
# - AWS Region: us-east-1
# - Parameter Environment: prod
# - Confirm changes before deploy: Y
# - Allow SAM CLI IAM role creation: Y
# - Save parameters to configuration file: Y
```

### 6. Update Frontend with API URL

After backend deployment, get the API Gateway URL:

```bash
# Get the API URL from CloudFormation outputs
aws cloudformation describe-stacks \
  --stack-name cloud-resume-challenge-backend \
  --query 'Stacks[0].Outputs[?OutputKey==`VisitorCountApiUrl`].OutputValue' \
  --output text
```

Update `frontend/script.js` with the actual API URL:

```javascript
const API_BASE_URL = 'https://your-actual-api-gateway-url.amazonaws.com/prod';
```

### 7. Deploy Frontend to S3

```bash
# Create S3 bucket for website
aws s3 mb s3://your-unique-bucket-name-cloud-resume

# Configure bucket for static website hosting
aws s3 website s3://your-unique-bucket-name-cloud-resume \
  --index-document index.html \
  --error-document index.html

# Upload website files
aws s3 sync frontend/ s3://your-unique-bucket-name-cloud-resume \
  --delete

# Set bucket policy for public read access
aws s3api put-bucket-policy \
  --bucket your-unique-bucket-name-cloud-resume \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::your-unique-bucket-name-cloud-resume/*"
      }
    ]
  }'
```

### 8. Set Up CloudFront Distribution

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config '{
    "CallerReference": "cloud-resume-challenge-'$(date +%s)'",
    "Comment": "Cloud Resume Challenge Website",
    "DefaultRootObject": "index.html",
    "Origins": {
      "Quantity": 1,
      "Items": [
        {
          "Id": "S3-cloud-resume-challenge",
          "DomainName": "your-unique-bucket-name-cloud-resume.s3-website-us-east-1.amazonaws.com",
          "CustomOriginConfig": {
            "HTTPPort": 80,
            "HTTPSPort": 443,
            "OriginProtocolPolicy": "http-only"
          }
        }
      ]
    },
    "DefaultCacheBehavior": {
      "TargetOriginId": "S3-cloud-resume-challenge",
      "ViewerProtocolPolicy": "redirect-to-https",
      "TrustedSigners": {
        "Enabled": false,
        "Quantity": 0
      },
      "ForwardedValues": {
        "QueryString": false,
        "Cookies": {
          "Forward": "none"
        }
      },
      "MinTTL": 0,
      "DefaultTTL": 86400,
      "MaxTTL": 31536000
    },
    "Enabled": true,
    "PriceClass": "PriceClass_100"
  }'
```

### 9. Set Up Custom Domain (Optional)

If you have a custom domain:

1. **Request SSL Certificate**:
```bash
aws acm request-certificate \
  --domain-name yourdomain.com \
  --validation-method DNS \
  --region us-east-1
```

2. **Validate Certificate**: Follow DNS validation steps in AWS Console

3. **Update CloudFront Distribution**: Add custom domain and certificate

4. **Update Route 53**: Create CNAME record pointing to CloudFront distribution

### 10. Test the Complete System

1. **Test API Endpoints**:
```bash
# Test GET request
curl https://your-api-gateway-url.amazonaws.com/prod/visitor-count

# Test POST request
curl -X POST https://your-api-gateway-url.amazonaws.com/prod/visitor-count
```

2. **Test Website**: Visit your CloudFront URL or custom domain

3. **Test Visitor Counter**: Refresh the page and verify the counter increments

### 11. Set Up CI/CD

The GitHub Actions workflows are already configured. They will:

- **Backend Pipeline**: Run tests, build, and deploy backend on push to main
- **Frontend Pipeline**: Validate, build, and deploy frontend on push to main

### 12. Write Blog Post

Document your experience and learnings:

- **Platforms**: Dev.to, Hashnode, Medium, or your own blog
- **Topics to cover**:
  - Challenges faced
  - AWS services learned
  - Best practices discovered
  - Lessons learned
  - Future improvements

## Architecture Overview

```
Internet → Route 53 → CloudFront → S3 (Static Website)
                ↓
            API Gateway → Lambda → DynamoDB (Visitor Count)
```

## Cost Optimization

- **DynamoDB**: Use on-demand billing (free tier: 25 GB storage, 25 RCU/WCU)
- **Lambda**: Free tier: 1M requests/month
- **API Gateway**: Free tier: 1M API calls/month
- **S3**: Free tier: 5 GB storage
- **CloudFront**: Free tier: 1 TB data transfer, 10M requests
- **Route 53**: $0.50/hosted zone/month

## Security Best Practices

1. **IAM**: Use least privilege principle
2. **S3**: Bucket policies for public read access only
3. **API Gateway**: CORS configuration
4. **Lambda**: Environment variables for configuration
5. **DynamoDB**: Point-in-time recovery enabled

## Monitoring and Logging

- **CloudWatch Logs**: Lambda function logs
- **CloudWatch Metrics**: API Gateway and Lambda metrics
- **DynamoDB**: CloudWatch metrics for table operations

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Check API Gateway CORS configuration
2. **403 Forbidden**: Verify S3 bucket policy
3. **Lambda Timeout**: Check function timeout settings
4. **DynamoDB Access**: Verify IAM permissions

### Debug Commands:

```bash
# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name cloud-resume-challenge-backend

# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/visitor-count

# Test DynamoDB table
aws dynamodb describe-table --table-name visitor-count-prod
```

## Next Steps

1. **Enhancements**:
   - Add more detailed analytics
   - Implement user authentication
   - Add contact form functionality
   - Implement caching strategies

2. **Advanced Features**:
   - Multi-region deployment
   - Blue-green deployments
   - Automated testing
   - Performance monitoring

3. **Portfolio**:
   - Document the project
   - Create a case study
   - Share on LinkedIn
   - Add to your resume

## Resources

- [AWS Cloud Resume Challenge](https://cloudresumechallenge.dev/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

**Congratulations!** You've successfully completed the AWS Cloud Resume Challenge. This project demonstrates real-world cloud engineering skills and is a great addition to your portfolio.
