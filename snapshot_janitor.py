import boto3
import sys
import time

def main():
	ec2_client=boto3.client('ec2')

	long_before=time.time()
	sys.stdout.write("Getting list of snapshots... ")
	dict_snapshots=ec2_client.describe_snapshots()
	long_after=time.time()
	int_duration=long_after-long_before
	print("done.")
	print(str(int_duration))

	print(str(type(dict_snapshots)))

main()