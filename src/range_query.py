import logging

logger = logging.getLogger(__name__)

def compile_range_query(compiler, data_length):
    @compiler.register_function('range_query')
    def range_query():

        from Compiler.types import sint, regint, Array, MemValue, sfix, cint
        from Compiler.library import print_ln, print_ln_to, do_while, for_range, if_

        # 设置定点数精度
        sfix.set_precision(32, 64)

        # 设置参与方数量和每方数据量, 0为查询方,1->silo为数据拥有方, radius为明文的查询半径
        volume = int(compiler.options.volume)

        radius = float(compiler.options.radius)
        distance = radius * radius

        def main():
            q_lng = sfix.get_input_from(0)
            q_lat = sfix.get_input_from(0)

            def game_loop(_=None):
                def type_run():
                    id = sint.get_input_from(1)
                    lng = sfix.get_input_from(1)
                    lat = sfix.get_input_from(1)
                    acc = sint(0)
                    acc += (lng - q_lng).square()
                    acc += (lat - q_lat).square()
                    acc -= distance
                    inside = (acc < 0)

                    @if_(inside.reveal())
                    def _():
                        # print_ln("%s", id.reveal())
                        if data_length == 3:
                            print_ln_to(1, "%s %s %s", id.reveal_to(1), lng.reveal_to(1), lat.reveal_to(1))
                        else:
                            print_ln_to(1, "%s", id.reveal_to(1))

                type_run()
                return True

            logger.info('run %d volume' % volume)
            for_range(volume)(game_loop)

        main()

    compiler.compile_func()