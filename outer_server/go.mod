module outer_server

go 1.18

replace transponder/connection => ../../transponder/connection
require transponder/connection v0.0.0
replace transponder/event => ../../transponder/event
require transponder/event v0.0.0
replace ConfigAdapter/JsonConfig => ../ConfigAdapter/JsonConfig
require ConfigAdapter/JsonConfig v0.0.0
