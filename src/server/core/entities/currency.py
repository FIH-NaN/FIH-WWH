from __future__ import annotations


from enum import Enum


class Currency(str, Enum):
		"""ISO 4217 currency codes for major world currencies."""
		
		# Major Reserve Currencies
		USD = "USD"  # United States Dollar
		EUR = "EUR"  # Euro
		GBP = "GBP"  # British Pound Sterling
		JPY = "JPY"  # Japanese Yen
		CHF = "CHF"  # Swiss Franc
		
		# Asia-Pacific
		CNY = "CNY"  # Chinese Yuan Renminbi
		HKD = "HKD"  # Hong Kong Dollar
		SGD = "SGD"  # Singapore Dollar
		AUD = "AUD"  # Australian Dollar
		NZD = "NZD"  # New Zealand Dollar
		INR = "INR"  # Indian Rupee
		KRW = "KRW"  # South Korean Won
		TWD = "TWD"  # Taiwan Dollar
		THB = "THB"  # Thai Baht
		MYR = "MYR"  # Malaysian Ringgit
		PHP = "PHP"  # Philippine Peso
		IDR = "IDR"  # Indonesian Rupiah
		VND = "VND"  # Vietnamese Dong
		PKR = "PKR"  # Pakistani Rupee
		BDT = "BDT"  # Bangladeshi Taka
		LKR = "LKR"  # Sri Lankan Rupee
		MMK = "MMK"  # Myanmar Kyat
		KHR = "KHR"  # Cambodian Riel
		LAK = "LAK"  # Lao Kip
		
		# North America
		CAD = "CAD"  # Canadian Dollar
		MXN = "MXN"  # Mexican Peso
		
		# South America
		BRL = "BRL"  # Brazilian Real
		ARS = "ARS"  # Argentine Peso
		CLP = "CLP"  # Chilean Peso
		COP = "COP"  # Colombian Peso
		PEN = "PEN"  # Peruvian Sol
		UYU = "UYU"  # Uruguayan Peso
		PYG = "PYG"  # Paraguayan Guarani
		BOB = "BOB"  # Bolivian Boliviano
		VES = "VES"  # Venezuelan Bolívar
		
		# Europe
		SEK = "SEK"  # Swedish Krona
		NOK = "NOK"  # Norwegian Krone
		DKK = "DKK"  # Danish Krone
		PLN = "PLN"  # Polish Zloty
		CZK = "CZK"  # Czech Koruna
		HUF = "HUF"  # Hungarian Forint
		RON = "RON"  # Romanian Leu
		BGN = "BGN"  # Bulgarian Lev
		HRK = "HRK"  # Croatian Kuna
		RSD = "RSD"  # Serbian Dinar
		ISK = "ISK"  # Icelandic Króna
		RUB = "RUB"  # Russian Ruble
		UAH = "UAH"  # Ukrainian Hryvnia
		BYN = "BYN"  # Belarusian Ruble
		MDL = "MDL"  # Moldovan Leu
		GEL = "GEL"  # Georgian Lari
		AMD = "AMD"  # Armenian Dram
		AZN = "AZN"  # Azerbaijani Manat
		TRY = "TRY"  # Turkish Lira
		
		# Middle East
		AED = "AED"  # UAE Dirham
		SAR = "SAR"  # Saudi Riyal
		ILS = "ILS"  # Israeli Shekel
		QAR = "QAR"  # Qatari Riyal
		KWD = "KWD"  # Kuwaiti Dinar
		BHD = "BHD"  # Bahraini Dinar
		OMR = "OMR"  # Omani Rial
		JOD = "JOD"  # Jordanian Dinar
		LBP = "LBP"  # Lebanese Pound
		IQD = "IQD"  # Iraqi Dinar
		IRR = "IRR"  # Iranian Rial
		
		# Africa
		ZAR = "ZAR"  # South African Rand
		EGP = "EGP"  # Egyptian Pound
		NGN = "NGN"  # Nigerian Naira
		KES = "KES"  # Kenyan Shilling
		MAD = "MAD"  # Moroccan Dirham
		TND = "TND"  # Tunisian Dinar
		GHS = "GHS"  # Ghanaian Cedi
		UGX = "UGX"  # Ugandan Shilling
		TZS = "TZS"  # Tanzanian Shilling
		ETB = "ETB"  # Ethiopian Birr
		MUR = "MUR"  # Mauritian Rupee
		ZMW = "ZMW"  # Zambian Kwacha
		BWP = "BWP"  # Botswana Pula
		MZN = "MZN"  # Mozambican Metical
		AOA = "AOA"  # Angolan Kwanza
		XOF = "XOF"  # CFA Franc BCEAO (West Africa)
		XAF = "XAF"  # CFA Franc BEAC (Central Africa)
		
		# Caribbean & Central America
		JMD = "JMD"  # Jamaican Dollar
		TTD = "TTD"  # Trinidad and Tobago Dollar
		BBD = "BBD"  # Barbadian Dollar
		XCD = "XCD"  # East Caribbean Dollar
		BSD = "BSD"  # Bahamian Dollar
		BZD = "BZD"  # Belize Dollar
		CRC = "CRC"  # Costa Rican Colón
		GTQ = "GTQ"  # Guatemalan Quetzal
		HNL = "HNL"  # Honduran Lempira
		NIO = "NIO"  # Nicaraguan Córdoba
		PAB = "PAB"  # Panamanian Balboa
		
		# Oceania
		FJD = "FJD"  # Fijian Dollar
		PGK = "PGK"  # Papua New Guinean Kina
		WST = "WST"  # Samoan Tala
		TOP = "TOP"  # Tongan Paʻanga
		VUV = "VUV"  # Vanuatu Vatu
		
		# Other Asian Currencies
		AFN = "AFN"  # Afghan Afghani
		BND = "BND"  # Brunei Dollar
		BTN = "BTN"  # Bhutanese Ngultrum
		KZT = "KZT"  # Kazakhstani Tenge
		KGS = "KGS"  # Kyrgyzstani Som
		TJS = "TJS"  # Tajikistani Somoni
		TMT = "TMT"  # Turkmenistani Manat
		UZS = "UZS"  # Uzbekistani Som
		MNT = "MNT"  # Mongolian Tögrög
		NPR = "NPR"  # Nepalese Rupee
		MVR = "MVR"  # Maldivian Rufiyaa

