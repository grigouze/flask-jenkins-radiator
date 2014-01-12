import socket
import urllib2
import json
import base64


class JenkinsCI(object):
    """
        The real class for get information in jenkins server
    """

    def __init__(self, url=None, username=None, password=None, view=None, timeout=0):
        if url is None:
            url = 'http://' + socket.gethostname()
        if view is None:
            view = ''
        else:
            view = '/view/%s' % view

        self.url = url
        self.username = username
        self.password = password
        self.view = view
        self.timeout = timeout

        return None

    def urlopen(self, url):
        """
            Binding to urllib2.urlopen
        """

        timeout = self.timeout
        request = urllib2.Request(url)
        
        if self.username:
        	base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        	request.add_header("Authorization", "Basic %s" % base64string)   

        return urllib2.urlopen(request, timeout=timeout)

    def get_all_jobs(self):
        """
            List all jobs of a view for the jenkins server
        """

        datas = self.urlopen('%s%s/api/json?tree=jobs[name,color]' % \
                (self.url, self.view))

        if not datas:
            raise ValueError(
                'Error getting build data from Jenkins server at %s' % \
                    self.url)

        ret = []

        jobs = json.loads(datas.read())
        for job in jobs['jobs']:
            newjob = {'name': job['name'], 'status': \
                self.translate_color_to_status(job['color']), 'blame': ''}
            if newjob['status'][0] in ('failed', 'unstable'):
                newjob['blame'] = self.get_blame_for(job['name'])

            ret.append(newjob)

        return ret

    @staticmethod
    def translate_color_to_status(color):
        """
            Translate color of jenkins to status for view
        """

        colors = {'blue': ['successful'], \
                'blue_anime': ['successful', 'building'], \
                'red': ['failed'], \
                'red_anime': ['failed', 'building'], \
                'yellow': ['unstable'], \
                'yellow_anime': ['unstable', 'building'], \
                'aborted': ['cancelled'], \
                'aborted_anime': ['cancelled', 'building'], \
                'disabled': ['disabled'], \
                'default': ['unknown']}

        return colors.get(color, colors.get('default'))

    def get_blame_for(self, jobname):
        """
            If you have to blame someone for bad work :)
        """

        datas = self.urlopen(
            "%s/job/%s/lastBuild/api/json?tree=culprits[fullName]" \
                % (self.url, jobname))

        culprits = json.loads(datas.read())

        if not culprits.get('culprits'):
            return "Unknown"

        return culprits['culprits'][0]['fullName']
