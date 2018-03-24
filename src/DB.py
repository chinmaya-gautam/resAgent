try:
    import mysql.connector
except ImportError:
    print "FATAL ERROR: mysql connector not installed\nsuggestion: pip install mysql-connector"


from resAgentConfig import *

class DB:
    def __init__(self):
        self.db_config = {
            'user': DB_USER,
            'password': DB_PASSWORD,
            'host': DB_HOST,
            'database': DB_NAME,
        }
        try:
            _conn = mysql.connector.connect(**self.db_config)
            c = _conn.cursor()
            ###############################################
            # SCHEMA: vmRecords
            #
            # This table contains records of vmStatus throughout a meeting
            # It is intended to be cleaned every midnight by a cron job (Not implemented yet)
            #
            # timestamp: timestamp for record
            # uuid: TABot/Job uuid
            # machine_ip: this VM's IP
            # client_type: SPARK/WEBEX
            # cpu_percent: percent cpu usage
            # cpu_percent_per_cpu: percent cpu usage per core
            # vmem_percent: percent virtual memory usage
            # smem_percent: percent swap memory usage
            # is_alive: if spark client is alive
            # is_logged_in: if a user is logged in
            # logged_in_user: spark user logged in
            # paired_device_id: device id of paired device if any
            # call_state: connected, disconnected, ringing or ringout
            # is_in_lobby: if user is waiting in lobby
            # media_stats: json dump of media statistics
            # packet_stats: json dump of packet statistics
            # res1: extra field for extra information
            #################################################

            query = '''
                   CREATE TABLE IF NOT EXISTS vmrecords (
                   row_id INT AUTO_INCREMENT PRIMARY KEY,
                   timestamp DATETIME,
                   uuid INT(10) unsigned zerofill,
                   machine_ip VARCHAR(32),
                   client_type VARCHAR(8),
                   cpu_percent FLOAT,
                   cpu_percent_per_cpu TEXT,
                   vmem_percent FLOAT,
                   smem_percent FLOAT,
                   is_alive VARCHAR(8),
                   is_logged_in VARCHAR(8),
                   logged_in_user VARCHAR(64),
                   paired_device_id TEXT,
                   call_state VARCHAR(32),
                   is_in_lobby VARCHAR(8),
                   media_stats JSON,
                   packet_stats JSON,
                   res1 TEXT
                   )
                   '''
            c.execute(query)
            _conn.commit()
            _conn.close()
        except Exception as e:
            print "Could not initate the database: %s" % (str(e))

    def dump(self, records):
        for record in records:
            print record

    def storeStatus(self, records):

        try:
            _conn = mysql.connector.connect(**self.db_config)
            c = _conn.cursor()
            query = '''
            INSERT INTO vmrecords (
            timestamp,
            uuid,
            machine_ip,
            client_type,
            cpu_percent,
            cpu_percent_per_cpu,
            vmem_percent,
            smem_percent,
            is_alive,
            is_logged_in,
            logged_in_user,
            paired_device_id,
            call_state,
            is_in_lobby,
            media_stats,
            packet_stats,
            res1 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            c.executemany(query, records)
            _conn.commit()
            _conn.close()
        except Exception as e:
            print "Could not store records to vmrecords table: %s" % (str(e))
