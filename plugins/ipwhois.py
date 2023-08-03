import requests
from utils.plugin import Plugin
from flask_classful import route
from flask import make_response, request


class IPWhois(Plugin):

    def _lookup_ip(self, ip_address):
      # Try get the ip data from the cache
      ip_data = self.cache_client.get_cache_item(ip_address)
      # If the entry expired then we'll resolve it
      if ip_data is None:
        ip_data = self._resolve_ip(ip_address)
        # Cache the response if we were able to resolve the IP.
        if ip_data is not None:
          self.cache_client.cache_item(ip_address, ip_data)
      # Return whatever we have for IP data and let the next guy deal with it :-)
      return ip_data

    def _resolve_ip(self, ip_address):
      ipwhois_io_response = requests.get(f"http://free.ipwhois.io/json/{ip_address}")
      if ipwhois_io_response.status_code == 200:
        return ipwhois_io_response.json()
      else:
        return None

    @route('/<ip_address>', methods=['GET', 'PURGE'])
    def ipwhois_ip_address(self, ip_address=None):
      if request.method == 'GET':
        ip_data = self._lookup_ip(ip_address)
        if ip_data is None:
          return make_response({}, 404)
        else:
          return ip_data
      if request.method == 'PURGE':
        self.cache_client.expire_cache_item(ip_address)
        return make_response({}, 204)
