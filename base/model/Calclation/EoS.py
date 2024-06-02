"""
形式は(格子体積, 温度) -> (圧力)で固定する
"""

# FIXME このモデルが入ってるフォルダが誤字ってる。Calclation -> Calculation

class EoS:
    """
    KCl:
    Dewaele et al., 2012: 
    """
    def KCl_dewaele2012(self, *,
                        V, T):
        P = V * T
        return P

    """
    Pt:
    
    """
    def Pt_anzellini2019(self, *,
                         V, T):
        P = V * T
        return P

    """
    Diamond:
    
    """


    """
    MgO:
    
    """

    """
    Au:
    
    """


    """
    FeO
    """