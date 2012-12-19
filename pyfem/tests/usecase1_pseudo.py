post Pl.pllwe
post Pl.plni
post Pl.plni2
post Usr.lwe
post Usr.sallysmith
post Usr.suziebell
post Cmp.ni
post Cmp.prggrp
post Cmp.kirmse
post Cmp.unit104
post Cmp.troop1031

put Usr.lwe.pars, $push, Cmp.ni, admin
put Usr.lwe.pars, $push, Pl.pllwe, home
put Cmp.ni.pars, $push, Pl.plni, office
put Cmp.prggrp.pars, $push, Cmp.ni, department
put Cmp.kirmse.pars, $push, Cmp.ni, department
put Cmp.unit104.pars, $push, Cmp.kirmse, area
put Cmp.troop1031.pars, $push, Cmp.unit104, unit
put Usr.sallysmith.pars, $push, Cmp.kirmse, admin
put Usr.sallysmith.pars, $push, Cmp.troop1031, troop_leader
put Usr.suziebell.pars, $push, Cmp.troop1031, brownie

# what will do? To children?
put Cmp.unit104.pars, $push, Pl.plni2, annex
# unit104 should see two Pl's:
    office: Pl.plni 
    annex: Pl.plni2


delete Usr.sallysmith.pars, $unset, Usr.sallysmith
put Usr.suziebell.pars.Cmp.troop1031, $set, role, troop_leader

get Cmp.troop1031.pars ??? cls==Pl # how to get Pl coming from ni

# get Places for Usr.lwe
get Usr.lwe.pars ??? cls==Pl

