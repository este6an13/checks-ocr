BANK_CODES = [
    "produbanco",
    "austro",
    "banecuador",
    "guayaquil",
    "internacional",
    "pichincha",
]

BOXES = {
    "produbanco": {
        "ACCOUNT_NAME": (0.5, 0.12, 0.04, 0.6),
        "ACCOUNT_NUMBER": (0.25, 0.05, 0.8, 0.08),
        "AMOUNT": (0.25, 0.06, 0.75, 0.25),
        "CHECK_NUMBER": (0.15, 0.08, 0.8, 0.11),
        "CLIENT_NAME": (0.55, 0.1, 0.18, 0.2),
        "PLACE_AND_DATE": (0.45, 0.06, 0.04, 0.45),
    },
    "austro": {
        "ACCOUNT_NAME": (0.5, 0.05, 0.05, 0.65),
        "ACCOUNT_NUMBER": (0.20, 0.05, 0.8, 0.00),
        "AMOUNT": (0.30, 0.10, 0.70, 0.2),
        "CHECK_NUMBER": (0.25, 0.15, 0.75, 0.10),
        "CLIENT_NAME": (0.55, 0.10, 0.15, 0.2),
        "PLACE_AND_DATE": (0.45, 0.05, 0.00, 0.5),
    },
    "banecuador": {
        "ACCOUNT_NAME": (0.5, 0.12, 0.04, 0.6),
        "ACCOUNT_NUMBER": (0.25, 0.1, 0.75, 0.05),
        "AMOUNT": (0.2, 0.1, 0.8, 0.2),
        "CHECK_NUMBER": (0.25, 0.1, 0.75, 0.15),
        "CLIENT_NAME": (0.55, 0.1, 0.18, 0.2),
        "PLACE_AND_DATE": (0.5, 0.1, 0.00, 0.5),
    },
    "guayaquil": {
        "ACCOUNT_NAME": (0.4, 0.05, 0.05, 0.70),
        "ACCOUNT_NUMBER": (0.2, 0.05, 0.06, 0.65),
        "AMOUNT": (0.25, 0.1, 0.75, 0.20),
        "CHECK_NUMBER": (0.25, 0.1, 0.75, 0.10),
        "CLIENT_NAME": (0.55, 0.1, 0.18, 0.2),
        "PLACE_AND_DATE": (0.45, 0.1, 0.04, 0.5),
    },
    "internacional": {
        "ACCOUNT_NAME": (0.4, 0.2, 0.05, 0.65),
        "ACCOUNT_NUMBER": (0.2, 0.05, 0.78, 0.05),
        "AMOUNT": (0.35, 0.15, 0.65, 0.20),
        "CHECK_NUMBER": (0.2, 0.1, 0.78, 0.1),
        "CLIENT_NAME": (0.50, 0.15, 0.18, 0.15),
        "PLACE_AND_DATE": (0.5, 0.1, 0.05, 0.5),
    },
    "pichincha": {
        "ACCOUNT_NAME": (0.5, 0.12, 0.04, 0.6),
        "ACCOUNT_NUMBER": (0.25, 0.05, 0.75, 0.1),
        "AMOUNT": (0.25, 0.10, 0.75, 0.2),
        "CHECK_NUMBER": (0.25, 0.1, 0.75, 0.15),
        "CLIENT_NAME": (0.55, 0.1, 0.18, 0.2),
        "PLACE_AND_DATE": (0.45, 0.1, 0.1, 0.5),
    },
}

COLUMNS_MAP = {
    "ACCOUNT_NUMBER": "NUMERO-CUENTA",
    "ACCOUNT_NAME": "NOMBRE-CUENTA",
    "CLIENT_NAME": "BENEFICIARIO",
    "CHECK_NUMBER": "CHEQUE",
    "AMOUNT": "VALOR",
}

BANK_NAMES = {
    "produbanco": "PRODUBANCO",
    "austro": "BANCO DEL AUSTRO",
    "banecuador": "BANECUADOR",
    "guayaquil": "BANCO GUAYAQUIL",
    "internacional": "BANCO INTERNACIONAL",
    "pichincha": "BANCO PICHINCHA",
}

CONFIDENCE_COLUMNS = [
    "FECHA",
    "NUMERO-CUENTA",
    "NOMBRE-CUENTA",
    "BENEFICIARIO",
    "CHEQUE",
    "VALOR",
    "CIUDAD",
]

COLUMNS = [
    "FECHA",
    "BANCO",
    "CIUDAD",
    "NUMERO-CUENTA",
    "NOMBRE-CUENTA",
    "BENEFICIARIO",
    "CHEQUE",
    "VALOR",
    "ID",
]
