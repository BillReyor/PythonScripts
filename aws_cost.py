import boto3
import datetime

# Constants
SECONDS_IN_HOUR = 3600
HOURS_IN_MONTH = 30 * 24

# Get EC2 instances
ec2 = boto3.resource('ec2')
instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

# AWS EC2 pricing information: https://aws.amazon.com/ec2/pricing/on-demand/
# Replace the instance pricing dict with up-to-date pricing information for your region
instance_pricing = {
    'c4.xlarge': 0.199, 
    't2.medium': 0.0464, 
    't2.micro': 0.0116,
    't2.small': 0.023,
    't3a.small': 0.0208,
    't3.xlarge': 0.1664,
    't3.2xlarge': 0.3328,
    't3.large': 0.0832,
    't2.micro': 0.0116,
    't2.medium': 0.0464,
    't2.large': 0.0928,
    'm5.large': 0.096,
    'c4.xlarge': 0.199,
    'c4.large': 0.1,
    'c3.4xlarge': 0.84,
    # Add more instance types and their pricing here
}

total_monthly_cost = 0

for instance in instances:
    instance_type = instance.instance_type
    instance_name = "N/A"
    for tag in instance.tags:
        if tag["Key"] == "Name":
            instance_name = tag["Value"]

    if instance_type in instance_pricing:
        hourly_cost = instance_pricing[instance_type]
        monthly_cost = hourly_cost * HOURS_IN_MONTH
        total_monthly_cost += monthly_cost
        print(f"Instance ID: {instance.id} | Name: {instance_name} | Type: {instance_type} | Monthly Cost: ${monthly_cost:.2f}")
    else:
        print(f"Instance ID: {instance.id} | Name: {instance_name} | Type: {instance_type} | Monthly Cost: Unknown instance type")

print(f"Total Monthly Cost: ${total_monthly_cost:.2f}")
