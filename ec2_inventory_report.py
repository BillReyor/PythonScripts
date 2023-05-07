import boto3
import csv

def get_all_regions():
    """
    Get a list of all AWS regions.

    Returns:
        A list of AWS region names.
    """
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    return regions

def get_ec2_instances(region):
    """
    Get a list of EC2 instances with their state as 'running' or 'stopped' in the specified region.

    Args:
        region: The AWS region to fetch instances from.

    Returns:
        A list of EC2 instances.
    """
    ec2 = boto3.resource('ec2', region_name=region)
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}])
    return instances

def write_inventory_to_csv(instances, csv_filename):
    """
    Write the inventory of EC2 instances to a CSV file.

    Args:
        instances: A list of EC2 instances.
        csv_filename: The name of the CSV file to write the inventory to.
    """
    fieldnames = ["Region", "Instance ID", "Instance Name", "Instance Type", "Instance State", "Owner"]

    with open(csv_filename, mode='a', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()

        # Iterate through instances and write their data to the CSV file
        for instance in instances:
            instance_id = instance.id
            instance_name = "N/A"
            instance_type = instance.instance_type
            instance_state = instance.state['Name']
            owner = "N/A"

            # Get the instance name and owner from the tags
            if instance.tags is not None:
                for tag in instance.tags:
                    if tag["Key"].lower() == "name":
                        instance_name = tag["Value"]
                    if tag["Key"].lower() == "owner":
                        owner = tag["Value"]

            # Write instance data to the CSV file
            csv_writer.writerow({
                "Region": instance.placement['AvailabilityZone'][:-1],
                "Instance ID": instance_id,
                "Instance Name": instance_name,
                "Instance Type": instance_type,
                "Instance State": instance_state,
                "Owner": owner,
            })

if __name__ == "__main__":
    csv_filename = "ec2_inventory.csv"
    regions = get_all_regions()

    for region in regions:
        instances = get_ec2_instances(region)
        write_inventory_to_csv(instances, csv_filename)

    print(f"EC2 inventory has been saved to {csv_filename}")
