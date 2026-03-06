
class FinancialObject:
		"""
		An abstract class, a financial object is an object that has a time series 
			data stored in the database.

		For instance, the asset: bank deposit is a financial object, where the 
			server store the users' bank deposit each period into a time series 
			database.

		user_id: every financial object should be bound to a user
		"""
		user_id: int


