class LightException(Exception):
	def __init__(self,code='',message='Error'):
		self.code = code
		self.message = message

	def __str__(self):
		return self.message

class EndpointExistsError(LightException):
	def __init__(self,message='Endpoint exist'):
		super(EndpointExistsError,self).__init__(message)

class URLExistError(LightException):
	def __init__(self,message='URL exists'):
		super(URLExistsError,self).__init__(message)
