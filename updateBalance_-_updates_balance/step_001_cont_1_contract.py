import smartpy as sp

class Contract(sp.Contract):
  def __init__(self):
    self.init(administrator = sp.address('tz1abmz7jiCV2GH2u81LRrGgAFFgvQgiDiaf'), balances = {}, paused = False, state = 0, tokenAddress = sp.address("KT1FAKEooooFAKEzSTATiCzSmartPyxCUdM4"), totalSupply = 0, underlyingBalance = 0)

  @sp.entry_point
  def approve(self, params):
    sp.set_type(params, sp.TRecord(spender = sp.TAddress, value = sp.TNat).layout(("spender", "value")))
    sp.if ~ (self.data.balances.contains(sp.sender)):
      self.data.balances[sp.sender] = sp.record(approvals = {}, balance = 0)
    sp.verify(~ self.data.paused)
    sp.verify((self.data.balances[sp.sender].approvals.get(params.spender, default_value = 0) == 0) | (params.value == 0), message = 'UnsafeAllowanceChange')
    self.data.balances[sp.sender].approvals[params.spender] = params.value

  @sp.entry_point
  def burn(self, params):
    sp.set_type(params, sp.TRecord(address = sp.TAddress, value = sp.TNat).layout(("address", "value")))
    sp.verify((sp.sender == self.data.administrator) | (sp.sender == sp.self_address))
    sp.verify(self.data.balances[params.address].balance >= params.value)
    self.data.balances[params.address].balance = sp.as_nat(self.data.balances[params.address].balance - params.value)
    self.data.totalSupply = sp.as_nat(self.data.totalSupply - params.value)

  @sp.entry_point
  def deposit(self, params):
    sp.set_type(params, sp.TNat)
    newTokens = sp.local("newTokens", params * 1000000000000000000)
    sp.if self.data.totalSupply != 0:
      newUnderlyingBalance = sp.local("newUnderlyingBalance", self.data.underlyingBalance + params)
      fractionOfPoolOwnership = sp.local("fractionOfPoolOwnership", (params * 1000000000000000000) // newUnderlyingBalance.value)
      newTokens.value = (fractionOfPoolOwnership.value * self.data.totalSupply) // sp.as_nat(1000000000000000000 - fractionOfPoolOwnership.value)
    self.data.underlyingBalance += params
    sp.transfer(sp.record(from_ = sp.sender, to_ = sp.self_address, value = params), sp.tez(0), sp.contract(sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))), self.data.tokenAddress, entry_point='transfer').open_some())
    sp.transfer(sp.record(address = sp.sender, value = newTokens.value), sp.tez(0), sp.contract(sp.TRecord(address = sp.TAddress, value = sp.TNat).layout(("address", "value")), sp.self_address, entry_point='mint').open_some())

  @sp.entry_point
  def getAdministrator(self, params):
    sp.set_type(sp.fst(params), sp.TUnit)
    __s9 = sp.local("__s9", self.data.administrator)
    sp.set_type(sp.snd(params), sp.TContract(sp.TAddress))
    sp.transfer(__s9.value, sp.tez(0), sp.snd(params))

  @sp.entry_point
  def getAllowance(self, params):
    __s10 = sp.local("__s10", self.data.balances[sp.fst(params).owner].approvals[sp.fst(params).spender])
    sp.set_type(sp.snd(params), sp.TContract(sp.TNat))
    sp.transfer(__s10.value, sp.tez(0), sp.snd(params))

  @sp.entry_point
  def getBalance(self, params):
    __s11 = sp.local("__s11", self.data.balances[sp.fst(params)].balance)
    sp.set_type(sp.snd(params), sp.TContract(sp.TNat))
    sp.transfer(__s11.value, sp.tez(0), sp.snd(params))

  @sp.entry_point
  def getTotalSupply(self, params):
    sp.set_type(sp.fst(params), sp.TUnit)
    __s12 = sp.local("__s12", self.data.totalSupply)
    sp.set_type(sp.snd(params), sp.TContract(sp.TNat))
    sp.transfer(__s12.value, sp.tez(0), sp.snd(params))

  @sp.entry_point
  def mint(self, params):
    sp.set_type(params, sp.TRecord(address = sp.TAddress, value = sp.TNat).layout(("address", "value")))
    sp.verify((sp.sender == self.data.administrator) | (sp.sender == sp.self_address))
    sp.if ~ (self.data.balances.contains(params.address)):
      self.data.balances[params.address] = sp.record(approvals = {}, balance = 0)
    self.data.balances[params.address].balance += params.value
    self.data.totalSupply += params.value

  @sp.entry_point
  def redeem(self, params):
    sp.set_type(params, sp.TNat)
    fractionOfPoolOwnership = sp.local("fractionOfPoolOwnership", (params * 1000000000000000000) // self.data.totalSupply)
    tokensToReceive = sp.local("tokensToReceive", (fractionOfPoolOwnership.value * self.data.underlyingBalance) // 1000000000000000000)
    self.data.underlyingBalance = sp.as_nat(self.data.underlyingBalance - tokensToReceive.value)
    sp.transfer(sp.record(address = sp.sender, value = params), sp.tez(0), sp.contract(sp.TRecord(address = sp.TAddress, value = sp.TNat).layout(("address", "value")), sp.self_address, entry_point='burn').open_some())
    sp.transfer(sp.record(from_ = sp.self_address, to_ = sp.sender, value = tokensToReceive.value), sp.tez(0), sp.contract(sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))), self.data.tokenAddress, entry_point='transfer').open_some())

  @sp.entry_point
  def setAdministrator(self, params):
    sp.set_type(params, sp.TAddress)
    sp.verify(sp.sender == self.data.administrator)
    self.data.administrator = params

  @sp.entry_point
  def setPause(self, params):
    sp.set_type(params, sp.TBool)
    sp.verify(sp.sender == self.data.administrator)
    self.data.paused = params

  @sp.entry_point
  def transfer(self, params):
    sp.set_type(params, sp.TRecord(from_ = sp.TAddress, to_ = sp.TAddress, value = sp.TNat).layout(("from_ as from", ("to_ as to", "value"))))
    sp.verify((sp.sender == self.data.administrator) | ((~ self.data.paused) & ((params.from_ == sp.sender) | (self.data.balances[params.from_].approvals[sp.sender] >= params.value))))
    sp.if ~ (self.data.balances.contains(params.to_)):
      self.data.balances[params.to_] = sp.record(approvals = {}, balance = 0)
    sp.verify(self.data.balances[params.from_].balance >= params.value)
    self.data.balances[params.from_].balance = sp.as_nat(self.data.balances[params.from_].balance - params.value)
    self.data.balances[params.to_].balance += params.value
    sp.if (params.from_ != sp.sender) & (~ (sp.sender == self.data.administrator)):
      self.data.balances[params.from_].approvals[sp.sender] = sp.as_nat(self.data.balances[params.from_].approvals[sp.sender] - params.value)

  @sp.entry_point
  def updateBalance(self, params):
    sp.set_type(params, sp.TUnit)
    sp.verify(self.data.state == 0, message = 'bad state')
    self.data.state = 1
    sp.transfer((sp.self_address, sp.self_entry_point('updateBalance_callback')), sp.tez(0), sp.contract(sp.TPair(sp.TAddress, sp.TContract(sp.TNat)), self.data.tokenAddress, entry_point='getBalance').open_some())

  @sp.entry_point
  def updateBalance_callback(self, params):
    sp.set_type(params, sp.TNat)
    sp.verify(sp.sender == self.data.tokenAddress, message = 'bad sender')
    sp.verify(self.data.state == 1, message = 'bad state')
    self.data.state = 0
    self.data.underlyingBalance = params