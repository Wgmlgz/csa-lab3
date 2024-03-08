(fn status int (
  (def (ready int))
  (io_status 0)
  (local_set ready)
  ready
))

(while (status) (
  (in 0)
  (out 1)
))
