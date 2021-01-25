import time

class StdWithTimeStamp:
    """Stamped stdout."""
    def __init__(self,std_out):
        self.old_out = std_out
        self.nl = True

    def write(self, x):
        """Write function overloaded."""
        if x == '\n':
            self.old_out.write(x)
            self.nl = True
        elif self.nl:
            self.old_out.write('%s %s' % (time.strftime("%Y-%m-%d %X"), x))
            self.nl = False
        else:
            self.old_out.write(x)
    
    def flush(self):
        pass