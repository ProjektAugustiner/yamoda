###
# <modulename>.coffee
# <description>
#
# @author dpausp (Tobias Stenzel)
#
###

###-- private module vars --###

MODULE_NAME = "<modulename>"
logg = undefined
that = undefined

###-- module functions --###


###-- READY --###

$ ->
  # module def
  that = yamoda.<modulename> = yamoda.make_module(MODULE_NAME,
    some_method: some_method
  )
  # other stuff to do
  logg = that.logg
  return

# vim: set filetype=coffee sw=2 ts=2 sts=2 expandtab: #
