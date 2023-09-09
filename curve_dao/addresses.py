from curve_dao.exceptions import CurveDaoOperationsError

CURVE_DAO_OWNERSHIP = {
    "agent": "0x40907540d8a6C65c637785e8f8B742ae6b0b9968",
    "voting": "0xE478de485ad2fe566d49342Cbd03E49ed7DB3356",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 30,
}

CURVE_DAO_PARAM = {
    "agent": "0x4eeb3ba4f221ca16ed4a0cc7254e2e32df948c5f",
    "voting": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 15,
}

EMERGENCY_DAO = {
    "forwarder": "0xf409Ce40B5bb1e4Ef8e97b1979629859c6d5481f",
    "agent": "0x00669DF67E4827FCc0E48A1838a8d5AB79281909",
    "voting": "0x1115c9b3168563354137cdc60efb66552dd50678",
    "token": "0x4c0947B16FB1f755A2D32EC21A0c4181f711C500",
    "quorum": 51,
}

VOTING_ESCROW = "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2"
veCRV = VOTING_ESCROW
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
CONVEX_VOTERPROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"
# 2-coin factory cryptopools only;
# tricrypto-ng factory admin is already the OWNERSHIP agent
CRYPTOSWAP_FACTORY_OWNER = "0x5a8fdC979ba9b6179916404414F7BA4D8B77C8A1"
STABLESWP_OWNER = "0xeCb456EA5365865EbAb8a2661B0c503410e9B347"
STABLESWAP_FACTORY_OWNER = "0x742C3cF9Af45f91B109a81EfEaf11535ECDe9571"
STABLESWAP_FACTORY_OWNER_2 = "0x768caA20Cf1921772B6F56950e23Bafd94aF5CFF"
STABLESWAP_GAUGE_OWNER = "0x519AFB566c05E00cfB9af73496D00217A630e4D5"

# checks if smart contract is whitelisted for veCRV
SMARTWALLET_CHECKER = "0xca719728Ef172d0961768581fdF35CB116e0B7a4"

# crvUSD controller factory
CONTROLLER_FACTORY = "0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC"

# Community Fund
COMMUNITY_FUND = "0xe3997288987E6297Ad550A69B31439504F513267"


def get_dao_voting_contract(vote_type: str):
    target = select_target(vote_type)
    return target["voting"]


def select_target(vote_type: str):
    if vote_type == "ownership":
        return CURVE_DAO_OWNERSHIP
    if vote_type == "parameter":
        return CURVE_DAO_PARAM
    if vote_type == "emergency":
        return EMERGENCY_DAO

    raise CurveDaoOperationsError(f"Vote type not recognized: {vote_type}")
