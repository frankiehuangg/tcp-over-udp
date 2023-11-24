from segment_flag import SegmentFlag


class Segment:
    def __init__(self, seq_num=0, ack_num=0):
        self.flags = SegmentFlag()
        self.seq_num = Segment.seq_num_counter
        self.ack_num = 0
        self.checksum = b""
        self.payload = b""

        Segment.seq_num_counter += 1

    
    @staticmethod
    def syn(seq_num: int):
        segment = Segment(seq_num=seq_num)
        segment.flags.set_syn()
        return segment
    
    @staticmethod
    def ack(seq_num: int):
        segment = Segment(seq_num=seq_num)
        segment.flags.set_ack()
        return segment
    
    @staticmethod
    def fin(seq_num: int):
        segment = Segment(seq_num=seq_num)
        segment.flags.set_fin()
        return segment
    
    @staticmethod
    def syn_ack(seq_num: int):
        segment = Segment(seq_num=seq_num)
        segment.flags.set_syn()
        segment.flags.set_ack()
        return segment
    
    @staticmethod
    def syn_fin(seq_num: int):
        segment = Segment(seq_num=seq_num)
        segment.flags.set_fin()
        segment.flags.set_ack()
        return segment


