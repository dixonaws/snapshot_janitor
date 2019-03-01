import boto3
import sys
import argparse
from botocore.exceptions import ClientError

def main():
	parser = argparse.ArgumentParser(
		description='Deletes snapshots that do not have an associated volume.')
	parser.add_argument('--destructive', help='destructive: delete snapshots or just list them', action='store_true')
	args = parser.parse_args()

	str_destructive = args.destructive

	print("snapshot_janitor v1.0, John Dixon (dixonaws@amazon.com)")
	print("https://github.com/dixonaws/snapshot_janitor")
	print("Example usage:")
	print("python3 snapshot_janitor.py [--destructive]")
	print("destructive: deletes snapshots that do not have an associated volume (otherwise just list snapshots that do not have a volume).")
	print("Arguments: --destructive=" + str(str_destructive))
	print("------")
	print()

	ec2_client=boto3.client('ec2')

	sys.stdout.write("Getting list of volumes... ")
	# describe_volumes returns ResponseMetadata and a list of Volumes
	dict_volumes_response=ec2_client.describe_volumes()

	list_volumes=dict_volumes_response['Volumes']

	list_volume_ids=[]

	for item in list_volumes:
		str_volume_id=item['VolumeId']
		list_volume_ids.append(str_volume_id)

	print("done (" + str(len(list_volumes)) + " volumes).")

	sys.stdout.write("Getting list of snapshots... ")
	# describe_snapshots returns a dict object with Snapshots (a list) and ResponseMetadata
	dict_snapshots_response=ec2_client.describe_snapshots(OwnerIds=['self'])
	list_snapshots = dict_snapshots_response['Snapshots']
	print("done (" + str(len(list_snapshots)) + " snapshots).")

	# declare a list of snapshots that we'll delete if destructive=True
	list_snapshots_to_delete=[]

	for snapshot in list_snapshots:
		str_volume_id=str(snapshot['VolumeId'])
		str_snapshot_id=str(snapshot['SnapshotId'])
		str_snapshot_desc=snapshot['Description']
		sys.stdout.write(str_snapshot_id + " (" + str_volume_id + "): " + str_snapshot_desc)
		try:
			if(list_volume_ids.index(str_volume_id)):
				sys.stdout.write(" (volume exists)")
			else:
				sys.stdout.write(" *** (no volume exists for this snapshot!)")
				list_snapshots_to_delete.append(str_snapshot_id)
		except ValueError:
			sys.stdout.write(" *** (no volume exists for this snapshot!)")
			list_snapshots_to_delete.append(str_snapshot_id)

		print()

	print()

	print("Snapshots to delete (" + str(len(list_snapshots_to_delete)) + " snapshots):")
	for snapshot in list_snapshots_to_delete:
		sys.stdout.write(snapshot + ", deleting... ")
		if(str_destructive==False):
			try:
				response=ec2_client.delete_snapshot(SnapshotId=snapshot, DryRun=True)
				print(response)
			except ClientError as e:
				print(e.response['Error']['Code'])

		if(str_destructive):
			try:
				response = ec2_client.delete_snapshot(SnapshotId=snapshot, DryRun=False)
				print(response)
			except ClientError as e:
				print(e.response['Error']['Code'])


main()