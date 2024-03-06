(
  (fn eq (a u64) (b u64) u64 (
    (local_get a)
    (sub_local b)
    (invert_bool)
    (local_set a)
    a))
  (fn add (a u64) (b u64) u64 (
    (local_get a)
    (add_local b)
    (local_set a)
    a))
  (fn sub (a u64) (b u64) u64 (
    (local_get a)
    (sub_local b)
    (local_set a)
    a))
    
  (fn mul (a u64) (b u64) u64 (
    (local_get a)
    (mul_local b)
    (local_set a)
    a))

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
      (local_set cur)))))
  
  ;; (fn ttt (n u64) u64 (if (eq n 0) 2 3))
  ;; (let a (if 0 2 3))
  ;; (let b (factorial 5))
  (let b (fib 18))
  ;; 0 1 1 2 3 5 8 13 21
  ;; 0 1 2 3 4 5 6 7  8  9
  ;; (print_u64 a)
  (print_u64 b)
  (halt)
)