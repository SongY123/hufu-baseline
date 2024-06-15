import logging

logger = logging.getLogger(__name__)

def compile_secret_sum(compiler):
    @compiler.register_function('secret_sum')
    def secret_sum():
        silo = int(compiler.options.n_clients)

        from Compiler.library import print_ln, for_range, if_, print_ln_to, start_timer, stop_timer
        from Compiler.types import sfix, sfix, cint, regint, Array, sint, Matrix
        # 设置定点数精度
        start_timer(1)

        count = sint.Array(silo - 1)

        @for_range(silo - 1)
        def _(i):
            count[i] = sint.get_input_from(i + 1)

        # 输出结果
        print_ln_to(0, "%s", sum(count[i] for i in range(silo - 1)).reveal_to(0))
        stop_timer(1)

    compiler.compile_func()