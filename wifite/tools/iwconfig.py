#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .dependency import Dependency

class Iwconfig(Dependency):
    dependency_required = True
    dependency_name = 'iw'
    dependency_url = 'apt-get install iw'

    @classmethod
    def mode(cls, iface, mode_name):
        """Set the mode of a wireless interface using iw command.
        
        Args:
            iface (str): Interface name (e.g., wlan0)
            mode_name (str): Mode to set (e.g., monitor, managed)
        
        Returns:
            int: Return code from the command execution
        """
        from ..util.process import Process
        # First bring the interface down
        Process(['ip', 'link', 'set', iface, 'down']).wait()
        # Set the mode using iw
        pid = Process(['iw', iface, 'set', 'type', mode_name])
        pid.wait()
        # Bring the interface back up
        Process(['ip', 'link', 'set', iface, 'up']).wait()
        return pid.poll()

    @classmethod
    def get_interfaces(cls, mode=None):
        """Get wireless interfaces, optionally filtered by mode.
        
        Args:
            mode (str, optional): Filter interfaces by this mode (e.g., monitor, managed)
        
        Returns:
            list: List of interface names matching the criteria
        """
        from ..util.process import Process
        interfaces = set()
        mode=mode.lower()
        # Get list of wireless interfaces
        (out, err) = Process.call('iw dev')
        if err:
            return list(interfaces)
        current_iface = None
        for line in out.split('\n'):
            line = line.strip()
            
            # Interface lines start with "Interface"
            if line.startswith('Interface'):
                current_iface = line.split('Interface')[1].strip()
            # If we're looking for a specific mode
            elif mode is not None and line.startswith('type'):
                current_mode = line.split('type')[1].strip()
                if current_mode == mode and current_iface:
                    interfaces.add(current_iface)
                    
            # If we're not filtering by mode, add all interfaces
            elif mode is None and current_iface:
                interfaces.add(current_iface)
                current_iface = None  # Reset for next interface
        print(interfaces)
        return list(interfaces)

    @classmethod
    def get_interface_info(cls, iface):
        """Get detailed information about a specific interface.
        
        Args:
            iface (str): Interface name to query
        
        Returns:
            dict: Dictionary containing interface information
        """
        from ..util.process import Process
        info = {}
        
        (out, err) = Process.call(['iw', 'dev', iface, 'info'])
        if err:
            return info

        for line in out.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()

        return info

