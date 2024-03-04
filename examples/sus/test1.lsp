(
  (fn eq (a u64) (b u64) u64 (
    (local_get a)
    (sub_local b)
    (invert_bool)
    (local_set a)
    (a)
  ))

  (fn sub (a u64) (b u64) u64 (
    (local_get a)
    (sub_local b)
    (local_set a)
    (a)
  ))


  ;; (fn fib (n u64) (
  ;;   (if (eq (n 0)) (0) (
  ;;     (if (eq (n 1)) (1) (
  ;;       fib
  ;;     ))
  ;;   ))
  ;; ))

  (fn print_u64 (n u64) (
    (let cur 100000000)
    (let base 10)
    (let zero 48)

    (while cur (
      (local_get n)
      (div_local cur)
      (rem_local base)
      (add_local zero)
      (out 1)

      (local_get cur)
      (div_local base)
      (local_set cur)
    )))
    )
  (fn add (a u64) (b u64) u64 (
    (local_get a)
    (add_local b)
    (local_set a)
    (a)
  ))

  (fn mul (a u64) (b u64) u64 (
    (local_get a)
    (mul_local b)
    (local_set a)
    (a)
  ))


  (fn factorial (n u64) u64  
    ((let r (if (eq n 0)
      (1)
       (mul n (factorial (sub n 1))   )
      ;;)
  )) (r)))
  (let a (factorial 1))
  (print_u64 (add (add (1) (2)) (2)))
  ;; (print_u64 (factorial 0))
  (halt)
)