from adcpreader.coroutine import coroutine, Coroutine
from adcpreader.rdi_writer import PARAMETERS, DEFAULT_PARAMETERS

class Header(Coroutine):
    ''' Coroutine showing header information of first ensemble 

    Including this coroutine in the pipeline displays the information contained
    in the fixed_leader of the first ensemble, and alters nothing to the ensemble
    itself.

    Parameters
    ----------
    header : str ('')
         header to be displayed before printing leader information.
    pause : bool (False)
         pauses processing after displaying information. Note that this
         cannot be used when files are processed automatically.
    
    '''
    def __init__(self, header = '', pause=False):
        super().__init__()
        self.coro_fun = self.coro_show_info()
        self.header = header
        self.pause = pause
        
    @coroutine
    def coro_show_info(self):
        first_time=True
        while True:
            try:
                ens = (yield)
            except GeneratorExit:
                break
            else:
                if first_time:
                    self.show_info(ens)
                    first_time = False
                self.send(ens)
        self.close_coroutine()

    def show_info(self, ens):
        print(f"ADCP configuration {self.header}")
        print("-"*80)
        for p in PARAMETERS['fixed_leader']:
            try:
                print(f"{p:20s} : {ens['fixed_leader'][p]}")
            except KeyError:
                pass
        print("\n")
        for section in DEFAULT_PARAMETERS.keys():
            if section=='fixed_leader':
                continue
            print(f"Variables in {section.replace('_',' ')}:")
            try:
                s = " - " .join(ens[section].keys())
            except KeyError:
                pass
            else:
                for line in self.wrapline(s):
                    print(f"\t{line}")
        if self.pause:
            input("Type <enter> to continue...")

    def wrapline(self, line, max_chars=75, marker=' - '):
        if len(line)<max_chars:
            return [line]
        else:
            lines = []
            while True:
                tmp = line[:max_chars]
                try:
                    idx = tmp.rindex(marker)
                except ValueError:
                    lines.append(tmp)
                    break
                else:
                    lines.append(tmp[:idx])
                    line = line[idx+len(marker):]
            return lines



class FileInfo(Coroutine):

    def __init__(self) -> None:
        super().__init__()
        self.coro_fun = self.process()


    @coroutine
    def process(self) -> None:
        while True:
            try:
                ens = (yield)
            except GeneratorExit:
                break
            else:
                #breakpoint()
                self.send(ens)
        self.close_coroutine()
