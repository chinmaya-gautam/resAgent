import re
from collections import OrderedDict
from datetime import datetime


__author__ = 'Ares Ou (weou@cisco.com)'


# monitor metrics constants
METRIC_OVERALL_CPU_USAGE = 'OVERALL_CPU_USAGE'
METRIC_OVERALL_MEMORY_USAGE = 'OVERALL_MEMORY_USAGE'
METRIC_MMP_CPU_USAGE = 'MMP_CPU_USAGE'

METRIC_FIELD_DATA = 'data'
METRIC_FIELD_MAX = 'max'
METRIC_FIELD_MIN = 'min'
METRIC_FIELD_AVERAGE = 'average'

MAX_RECORDS_PER_METRIC = 3600

REGEX_TOP_CPU_IDLE = re.compile(r',[ ]*([\d.]*)[% ]*id,')
REGEX_FREE_MEMORY_USAGE = re.compile(r'Mem:[ ]*([\d]*)[ ]*([\d]*)[ ]*([\d]*)[ ]*([\d]*)[ ]*([\d]*)[ ]*([\d]*)')
REGEX_TOP_CPU_IDLE_WITH_NO = re.compile(r'[CPUcpu]*(\d)*[ ]*:[ ]*.*?,[ ]*([\d.]*)[% ]*id,')


class SamplerBase(object):
    METRIC_NAME = None

    @classmethod
    def add_record(cls, data, data_dict, sample_time):
        data_dict[cls.METRIC_NAME][METRIC_FIELD_DATA][sample_time] = data

    @classmethod
    def update_average(cls, data, data_dict, old_len, removed_value=0):
        # Update average value, should be done after the max records check
        data_dict[cls.METRIC_NAME][METRIC_FIELD_AVERAGE] = round(
            ((data_dict[cls.METRIC_NAME][METRIC_FIELD_AVERAGE] * old_len + data - removed_value)
             / len(data_dict[cls.METRIC_NAME][METRIC_FIELD_DATA])), 2)

    @classmethod
    def check_records_exceed_max(cls, data_dict):
        # Check if records exceeds max
        if len(data_dict[cls.METRIC_NAME][METRIC_FIELD_DATA]) > MAX_RECORDS_PER_METRIC:
            # The pairs are returned in LIFO order if last is true or FIFO order if false.
            return data_dict[cls.METRIC_NAME][METRIC_FIELD_DATA].popitem(last=False)
        else:
            return None, None

    @classmethod
    def set_records_limit(cls,max_record_num):
        MAX_RECORDS_PER_METRIC = max_record_num

    @classmethod
    def sample(cls, ssh_client):
        raise NotImplementedError
    
    @classmethod
    def put_data(cls, data, data_dict):
        """Put data into the corresponding dictionary, update min
        or max by default.
        """
        sample_time = datetime.now().strftime("%y%m%d%H%M%S.%f")

        if cls.METRIC_NAME not in data_dict:
            data_dict[cls.METRIC_NAME] = {
                METRIC_FIELD_DATA: OrderedDict({sample_time: data}),
                METRIC_FIELD_AVERAGE: data,
            }
        elif data is not None:
            old_len = len(data_dict[cls.METRIC_NAME][METRIC_FIELD_DATA])
            cls.add_record(data, data_dict, sample_time)

            key, value = cls.check_records_exceed_max(data_dict)
            if value is not None:
                cls.update_average(data, data_dict, old_len, value)
            else:
                cls.update_average(data, data_dict, old_len)

    @classmethod
    def _get_command_stdout(cls, ssh_client, command):
        stdin, stdout, stderr = ssh_client.exec_command(command)
        return stdout.read()


class OverallCPUUsageSampler(SamplerBase):
    METRIC_NAME = METRIC_OVERALL_CPU_USAGE

    @classmethod
    def sample(cls, ssh_client):
        """Sampling overall CPU usage of all cores combined with `top` command."""
        command = '[ -f ~/.toprc ] && yes | mv ~/.toprc ~/.toprc.bak; ' \
                  'top -bn2 -d 0.2 | grep "Cpu(s)" | tail -n1; ' \
                  'yes | mv ~/.toprc.bak ~/.toprc'
        match = REGEX_TOP_CPU_IDLE.search(cls._get_command_stdout(ssh_client, command))

        if match:
            return 100.00 - round(float(match.group(1)), 2)
        else:
            return None


class OverallMemoryUsageSampler(SamplerBase):
    METRIC_NAME = METRIC_OVERALL_MEMORY_USAGE

    @classmethod
    def sample(cls, ssh_client):
        """Sampling overall memory usage, extracting `used` column from the result
        of `free` command. Unit is MB.
        """
        command = 'free -m | grep "Mem:"'
        # the headers are "total       used       free     shared    buffers     cached"
        match = REGEX_FREE_MEMORY_USAGE.search(cls._get_command_stdout(ssh_client, command))

        if match:
            return int(match.group(2))
        else:
            return None


class MMPCPUUsageSampler(SamplerBase):
    METRIC_NAME = METRIC_MMP_CPU_USAGE

    @classmethod
    def sample(cls, ssh_client):
        """Sampling MMP server CPU usage, will read all threads in the MMP process
        and parse the usage.
        """
        # check if the rc file for top exists, back up the original one and create a new one
        # with desired configuration. Then top will load our customized settings. After
        # sampling, restore the original file.
        # TODO: add back user filter when finished debugging
        command = '[ -f ~/.toprc ] && yes | mv ~/.toprc ~/.toprc.bak; ' \
                  'echo -en \'RCfile for "top with windows"\nId:a, Mode_altscr=0, Mode_irixps=1, Delay_time=3.000, ' \
                  'Curwin=0\nDef    fieldscur=AEHIOQTWKNMbcdfgjplrsuvyzX\n' \
                  '        winflags=95545, sortindx=10, maxtasks=0\n' \
                  '        summclr=1, msgsclr=1, headclr=3, taskclr=1\n\' >> ~/.toprc;' \
                  ' top -bn2 -d 0.1;' \
                  ' yes | rm ~/.toprc; mv ~/.toprc.bak ~/.toprc'

        result = cls._get_command_stdout(ssh_client, command).split('\n')
        data = ''

        for line in result[len(result) / 2:]:
            match = REGEX_TOP_CPU_IDLE_WITH_NO.search(line)

            if match:
                data += 'CPU%d: %f | ' % (int(match.group(1)), 100.0 - round(float(match.group(2)), 2))
            else:
                parts = line.split()
                if parts and parts[-1] in ['NETWORK', 'SESSION']:
                    data += parts[-1] + ' ' + parts[8] + ' | '
        return data

    @classmethod
    def put_data(cls, data, data_dict):
        sample_time = datetime.now().strftime("%y%m%d%H%M%S.%f")

        if cls.METRIC_NAME not in data_dict:
            data_dict[cls.METRIC_NAME] = {
                METRIC_FIELD_DATA: OrderedDict({sample_time: data}),
                METRIC_FIELD_MAX: None,
                METRIC_FIELD_MIN: None,
                METRIC_FIELD_AVERAGE: None,
            }
        else:
            cls.add_record(data, data_dict, sample_time)
            _, _ = cls.check_records_exceed_max(data_dict)


METRIC_TO_SAMPLING = {
    METRIC_OVERALL_CPU_USAGE: OverallCPUUsageSampler,
    METRIC_OVERALL_MEMORY_USAGE: OverallMemoryUsageSampler,
    METRIC_MMP_CPU_USAGE: MMPCPUUsageSampler,
}
