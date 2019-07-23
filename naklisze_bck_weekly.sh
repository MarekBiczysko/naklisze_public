ckup django db script.
#
####################################

# What to backup.
mysqldump naklisze > /tmp/naklisze_db_bck
backup_files="/tmp/naklisze_db_bck /etc/supervisor/conf.d/sklep.conf /root/camera_shop/nginx.conf /root/camera_shop/cert_renew.bash /root/camera_shop/update_all.bash /root/camera_shop/unicorn_start.bash /root/camera_shop/static_cdn /root/camera_shop/naklisze_bck_daily.sh /root/camera_shop/naklisze_bck_weekly.sh"

# Where to backup to.
dest="/home/naklisze_bck_weekly"

# Create archive filename.
thedate=$(date +%Y-%M-%d)
archive_file="naklisze-$thedate.tgz"

# Print start status message.
echo "Backing up $backup_files to $dest/$archive_file"
date
echo

# Backup the files using tar.
tar czf $dest/$archive_file $backup_files

# Print end status message.
echo
echo "Backup finished"
date

# Long listing of files in $dest to check file sizes.
ls -lh $dest

# delete old files if > 4 files
cd $dest
ls -t | sed -e '1,4d' | xargs -d '\n' rm
ls -la
