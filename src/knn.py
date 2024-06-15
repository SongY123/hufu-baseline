import logging

logger = logging.getLogger(__name__)

def compile_knn(compiler, data_length):
    @compiler.register_function('knn')
    def knn():
        MAX_DISTANCE = 9999
        # 设置参与方数量和每方数据量, 0为查询方,1->silo为数据拥有方, k为kNN的参数
        silo = int(compiler.options.n_clients)
        volume = int(compiler.options.volume)
        k = int(compiler.options.k)

        from Compiler.library import for_range, if_, print_ln_to, start_timer, stop_timer
        from Compiler.types import sfix, cint, sint
        # 设置定点数精度
        sfix.set_precision(16, 32)

        def main():
            # 查询方0输入查询数据
            q_lng = sfix.get_input_from(0)
            q_lat = sfix.get_input_from(0)
            k_player_array = cint.Array(k)
            k_id_array = sint.Array(k)
            k_lng_array = sint.Array(k)
            k_lat_array = sint.Array(k)

            k_distance_array = sfix.Array(k)
            k_distance_array.assign_all(MAX_DISTANCE)

            def game_loop(_=None):
                def type_run():
                    @for_range(silo - 1)
                    def _(i):
                        id = sint.get_input_from(i + 1)
                        lng = sfix.get_input_from(i + 1)
                        lat = sfix.get_input_from(i + 1)
                        distance = (lng - q_lng).square() + (lat - q_lat).square()
                        max_k = cint(0)
                        for kk in range(1, k):
                            t = (k_distance_array[max_k] < k_distance_array[kk]).if_else(1, 0)

                            @if_(t.reveal() == 1)
                            def _():
                                max_k.update(kk)
                        t = (distance < k_distance_array[max_k]).if_else(1, 0)

                        @if_(t.reveal() == 1)
                        def _():
                            k_player_array[max_k] = i
                            k_id_array[max_k] = id
                            k_distance_array[max_k] = distance
                            k_lng_array[max_k] = lng
                            k_lat_array[max_k] = lat

                type_run()
                return True

            logger.info('run %d volume' % volume)
            for_range(volume)(game_loop)

            @for_range(k)
            def _(i):
                player_id = k_player_array[i] + 1
                if data_length == 3:
                    print_ln_to(player_id, "%s %s %s", k_id_array[i].reveal_to(player_id),
                                k_lng_array[i].reveal_to(player_id), k_lat_array[i].reveal_to(player_id))
                else:
                    print_ln_to(player_id, "%s", k_id_array[i].reveal_to(player_id))

        start_timer(1)
        main()
        stop_timer(1)

    compiler.compile_func()