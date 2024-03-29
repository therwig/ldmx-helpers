""" Module for looping through event trees in python-based analyses

Examples
--------
    
    from LDMX.Analysis import EventTree

    event_tree = EventTree.EventTree('my_events.root')

    for event in event_tree :
        event.EventHeader.Print()
        event.SimParticles # can ignore pass name if only one collection
    #loop over events

"""

import ROOT

if ROOT.gSystem.Load('libFramework.so') != 0 :
    print('[ WARN ] : Could not import event dictionary!')
    print('           Looping through event trees may not work.')

class EventTree :
    """Wrapper class for ROOT's TTree

    Parameters
    ----------
    event_file : str
        Full path to event file with events to load

    Attributes
    ----------
    __file : ROOT.TFile
        loaded in, read-only file
    __tree : ROOT.TTree
        event tree retrieved from file
    __index : int
        Current index in TTree
    __unclaimed_branches : list of str
        List of branches in the TTree that haven't been cached yet
    __claimed_branches : dict of str to str
        Dictionary of short names to full branch names that are cached
    """

    def __init__(self, event_file) :
        self.__file = ROOT.TFile(event_file)
        self.__tree = self.__file.Get("LDMX_Events")
        self.__index = 0

        self.__unclaimed_branches = [b.GetName() for b in self.__tree.GetListOfBranches()]
        self.__claimed_branches = { 'EventHeader' : 'EventHeader' }

    def __iter__(self) :
        """The Tree is it's own iterator"""
        return self

    def __next__(self) :
        """Go to the next event"""
        if self.__index < self.__tree.GetEntriesFast() :
            self.__tree.GetEntry(self.__index)
            self.__index += 1
            return self

        raise StopIteration

    def __getattr_claimed__(self, name) :
        """Internal function for getting a branch without checking"""
        return getattr(self.__tree, self.__claimed_branches[name])

    def __getattr__(self, name) :
        """Get an event object

        If a full branch name (with pass) is not specified,
        we look for any branch name matching. If multiple
        branch names match, we throw an exception.

        This custom function is only called **after** other
        attempts to get an attribute have failed. i.e. Unless
        an attribute has been inserted into __dict__ using the setattr
        method, we will assume that the user is trying to get a
        branch from the tree.

        Parameters
        ----------
        name : str
            Name of branch (pass optional if only one branch)
        """

        # check for cached name -> full name first
        #   EventHeader is put into this dictionary in __init__
        if name in self.__claimed_branches :
            return self.__getattr_claimed__(name)

        found=False
        for candidate in self.__unclaimed_branches :
            if name in candidate:
                if found :
                    raise AttributeError(f'More than one branch matching \'{name}\'.')
                found=True
                self.__claimed_branches[name] = candidate

        if found :
            self.__unclaimed_branches.remove(self.__claimed_branches[name])
            return self.__getattr_claimed__(name)
        else :
            raise AttributeError(f'No branch matching \'{name}\'.')
