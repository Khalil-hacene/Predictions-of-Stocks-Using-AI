"""Curated equity universe based on Nasdaq's published Nasdaq-100 constituents."""

NASDAQ_100_SOURCE = "https://www.nasdaq.com/articles/global-indexes/nasdaq-100-index"

STOCKS = (
    ("AAPL", "Apple"), ("ABNB", "Airbnb"), ("ADBE", "Adobe"), ("ADI", "Analog Devices"),
    ("ADP", "Automatic Data Processing"), ("ADSK", "Autodesk"), ("AEP", "American Electric Power"),
    ("ALAB", "Astera Labs"), ("ALNY", "Alnylam Pharmaceuticals"), ("AMAT", "Applied Materials"),
    ("AMD", "Advanced Micro Devices"), ("AMGN", "Amgen"), ("AMZN", "Amazon"), ("APP", "AppLovin"),
    ("ARM", "Arm Holdings"), ("ASML", "ASML Holding"), ("AVGO", "Broadcom"), ("AXON", "Axon Enterprise"),
    ("BKNG", "Booking Holdings"), ("BKR", "Baker Hughes"), ("CCEP", "Coca-Cola Europacific Partners"),
    ("CDNS", "Cadence Design Systems"), ("CEG", "Constellation Energy"), ("CMCSA", "Comcast"),
    ("COST", "Costco"), ("CPRT", "Copart"), ("CRWD", "CrowdStrike"), ("CRWV", "CoreWeave"),
    ("CSCO", "Cisco"), ("CSX", "CSX"), ("CTAS", "Cintas"), ("DASH", "DoorDash"), ("DDOG", "Datadog"),
    ("DXCM", "Dexcom"), ("EXC", "Exelon"), ("FANG", "Diamondback Energy"), ("FAST", "Fastenal"),
    ("FER", "Ferrovial"), ("FTNT", "Fortinet"), ("GEHC", "GE HealthCare"), ("GILD", "Gilead Sciences"),
    ("GOOG", "Alphabet Class C"), ("GOOGL", "Alphabet Class A"), ("HON", "Honeywell"),
    ("HONA", "Honeywell Aerospace"), ("IDXX", "IDEXX Laboratories"), ("INTC", "Intel"), ("INTU", "Intuit"),
    ("ISRG", "Intuitive Surgical"), ("KDP", "Keurig Dr Pepper"), ("KHC", "Kraft Heinz"), ("KLAC", "KLA"),
    ("LIN", "Linde"), ("LITE", "Lumentum"), ("LRCX", "Lam Research"), ("MAR", "Marriott"),
    ("MCHP", "Microchip Technology"), ("MDLZ", "Mondelez"), ("MELI", "MercadoLibre"),
    ("META", "Meta Platforms"), ("MNST", "Monster Beverage"), ("MPWR", "Monolithic Power Systems"),
    ("MRVL", "Marvell Technology"), ("MSFT", "Microsoft"), ("MSTR", "Strategy"), ("MU", "Micron Technology"),
    ("NBIS", "Nebius Group"), ("NFLX", "Netflix"), ("NVDA", "NVIDIA"), ("NXPI", "NXP Semiconductors"),
    ("ODFL", "Old Dominion Freight Line"), ("ORLY", "O'Reilly Automotive"),
    ("PANW", "Palo Alto Networks"), ("PAYX", "Paychex"), ("PCAR", "PACCAR"), ("PDD", "PDD Holdings"),
    ("PEP", "PepsiCo"), ("PLTR", "Palantir"), ("PYPL", "PayPal"), ("QCOM", "Qualcomm"),
    ("REGN", "Regeneron Pharmaceuticals"), ("RKLB", "Rocket Lab"), ("ROP", "Roper Technologies"),
    ("ROST", "Ross Stores"), ("SBUX", "Starbucks"), ("SHOP", "Shopify"), ("SNDK", "SanDisk"),
    ("SNPS", "Synopsys"), ("SPCX", "Space Exploration Technologies"), ("STX", "Seagate Technology"),
    ("TER", "Teradyne"), ("TMUS", "T-Mobile US"), ("TRI", "Thomson Reuters"), ("TSLA", "Tesla"),
    ("TTWO", "Take-Two Interactive"), ("TXN", "Texas Instruments"), ("VRTX", "Vertex Pharmaceuticals"),
    ("WBD", "Warner Bros. Discovery"), ("WDAY", "Workday"), ("WDC", "Western Digital"),
    ("WMT", "Walmart"), ("XEL", "Xcel Energy"),
)

assert len(STOCKS) >= 100 and len({symbol for symbol, _ in STOCKS}) == len(STOCKS)
