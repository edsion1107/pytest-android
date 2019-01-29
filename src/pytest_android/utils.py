#!/usr/bin/env python
# encoding: utf-8

"""
@author: edsion
@file: others.py
@time: 2019-01-12 16:04
"""
import base64
from io import BytesIO

try:
    from PIL import Image, ImageDraw
except ImportError:
    pass
MARKER_RESIZE = 1 / 12  # 图标（水印）相对于截图的大小
MARKER_OFFSET_X = 1 / 4  # X轴图标（水印）坐标修正比例
MARKER_OFFSET_Y = 1 / 4  # Y轴图标（水印）坐标修正比例

# 用base64储存水印图标，避免资源可能丢失（误删）的情况，还能减少磁盘I/O
CLICK_ICON = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAG" \
             "7AAABuwBHnU4NQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAB68SURBVHic7Z15tF9Fle8/SUgIiEwBgtgIKg" \
             "E2kJIwiAMokAYH0LZpsGkUBQ3jE0LCIAJG8gDDPD0RBEQmbWdtaBsFEgSfTwTFUBA2Kk8EoUUIoMwxJOk/6tzk3nCHU+dX53fO+Z39" \
             "Weu3stZNDXsld39/Vbuq9h61bNkyDMNoJ6OrNsAwjOowATCMFrNK1Qb0Kk7kRGBOzubXeNWDSjTHMAbFVgCG0WJMAAyjxZgAGEaLMQ" \
             "EwjBZjAmAYLcYEwDBajAmAYbQYEwDDaDEmAIbRYkwADKPFmAAYRosxATCMFmMCYBgtxgTAMFqMCYBhtBgTAMNoMSYAhtFiTAAMo8WY" \
             "ABhGi6mdADiRDZ3IFlXbYRhtoFYC4EQmArcBP3UiW1Ztj2H0OrURgH7OvyWwIXCbE5FqrTJGwolMdiLTq7bDKEYtBCBz/nlAf4c3Ea" \
             "g5TmQyMBe4MEuDbjSMygXAiWxAcP6tBvnriZgI1JJ+zr9+9qM5JgLNo1IBGMH5++gTgeHaGF1kEOfvw0SgYVQmAE5kfYLzb52j+URg" \
             "nolA9Qzj/H2YCDSISgQg0vn7MBGomBzO34eJQEOoagUwDdimQD/bDlREhPP3YSLQAKoSgDOBywr23YAgAjGrB6MDCjh/HyYCNacSAf" \
             "Cqy4Aj6UwE5pkIlE8Hzt/HAU5ktYQmGQmpLAjYTwS+UnAIE4GSSeD89wFTverL6awyUlLpMWAmAkfQmQjc5kSKxBOMYUjo/E+ls8pI" \
             "TeUXgfqJwOUFh1ifsBIwEUiEOX97qFwAYLkIHI6JQOWY87eLWggADBCBKwoOYSLQIeb87aM2AgDLReAwOheByemsagfm/O2kVgIAA0" \
             "TgyoJDmAhEYs7fXmonALBcBA6luAish4lALsz5200tBQCSioBLZ1VvYc5v1FYAYIAIfLXgEOsBc00EXos5vwE1FwBYLgKHYCKQDHN+" \
             "o4/aCwAMEIGrCg7Rtx14Wzqrmok5v9GfRggALBeBaRQXgQmElUBrRcCc31iZVao2IAavusyJTANGAQcXGKJPBKZ61XvTWvcabgVeyd" \
             "n2gTINAXN+Y3BGLVu2rGobonEiowmnA0VEAOBp4B+96vx0VtUXc35jKBqzBeiPV11K2A5cXXCICcCtTmTbZEbVFHN+YzgaKQCwXAQ+" \
             "TWciMLeXRcCc3xiJxgoAJBGBdelRETDnN/LQaAGAASJwTcEh+kRgSjqrqsWc38hL4wUAlovAp+hMBG7tBREw5zdiaOQpwFBkpwNfAz" \
             "5RcIhngF296n3prOoe5vxGLD2xAugjWwkcDFxbcIhHgMfTWdQ9zPmNIvSUAMAAEbgusut8wt2AZ9JbVS7m/EZRek4AYLkIHER+EZhP" \
             "cIDGOX/GjoT3DkUw528xPSkAMEAErh+h6b009Ju/D696FfC/gNiAjjl/y+lZAYDlIvBJhhYBT3CAp7tnVTl41UuJEwFzfqO3BQCGFY" \
             "Gecf4+IkTAnN8AWiAAMEAEvp79qM8BFlZnVTnkEAFzfmM5PXUPYCScyBjgVOCiXnT+/jiRI4BLCE+n+zDnNwbQKgFoGyuJgDm/8RpM" \
             "AHqcTAQOJ5x0mPMbAzABaAFOZJxX/XvVdhj1wwTAMFpMK04BDMMYHBMAw2gxJgCG0WJMAAyjxZgAGEaLMQEwjBZjAmAYLcYEwDBajA" \
             "mAYbQYEwDDaDEmAIbRYkwADKPFmAAYRotZZaQGTmRNYKsu2JIS71VfqtqIPDiRscCmwGrAQmBhFU93ncgoYKduz9shf/CqT1ZtRJMZ" \
             "UQCA7YDbyjYkMVMIuf5rhROZCOwPbAlsBrwVeBMwZqV2jwE/A+4AbvSq3ahWtCrwiy7Mk5IjgMuqNqLJ5BEAo0OcyE7AUcB+wLgcXf" \
             "4B+Lfsc5ETuQ44y6v+vjwrjTZiAlASTmQc4dv+M4TKPUUZRyh/frAT+Q4wx6vem8BEw7AgYBk4ke0JW5Br6Mz5+zMa+FdgvhO5zomM" \
             "TzSu0WJMABLiRFZxIrOAOwEpcaqPA7c5kQ1KnMNoASYAiXAi6xICd7PpztbqHcAvnUjTTmiMGmECkAAnMoFQnvsdXZ56U+D/OZFduz" \
             "yv0SOYAHSIE1kPmAdsW5EJawHfdSIbVTS/0WBMADrAiYwGfgi4ik2ZAFydXeYxjNyYAHTG0cC7qzYiYw+CPYaRmzzBqleAR8o2JDGl" \
             "X6V1Im8Fzkg03IuEar5rdDjOmU7kFq/6QIG+y2je//PzVRvQdKwyUEGcyPeBfy7YfTHwXeA6YAHwp+znmwDbAAcSbg0WWdLP86pTC9" \
             "pltAwTgAI4kQ0JTht73LcUuAC4YKT7/U7EARcCuxUwcR+v+oMC/YyWYTGAYnySeOdfCLzfqx6X53GPV/XAnsBVBew7z4msWqCf0TJM" \
             "AIpxUGT7u4ApXvWWmE5e9VWv+mniReDNwLGRfYwWYluASLJv1pfJvz9/EZjkVf/cwZyvI7wt2Cyi24vAFl16Smw0FFsBxLMxccG5cz" \
             "pxfgCv+iLh7XsMrwPO6mReo/cxAYhn44i2zwHnppjUq95KuHQUwwFO5J0p5jd6ExOAeGIE4NHs2zsVxwKLItqPAi62G4LGUJgAxPOG" \
             "iLYLU07sVf8AnB/ZbQfig5ZGSzABiOcvEW03LWH+LwKxMYU5WXJXwxiACUA8MXn5NnUi66ec3Ku+AHw2sttE4JSUdhi9gQlAPA9Ftv" \
             "+3Emy4HvhlZJ/pTmRSCbYYDcYEIBKv+hfiHqEcnT0bTmnDMsLLv5hLHOOIjx8YPY4JQDF+FtH2rcCHUhvgVe8Cro3strcTeX9qW4zm" \
             "YgJQjH+PbH9q6lVAxonEP4m9IKtGZBgmAAX5IeE6cF62BaalNsKrPkF8ToItCbUKDMPeAhTFiXyTkKc/LwsJbwL+mtiOcYScAjHvBP" \
             "6W2fJUSluajhMZQzgx2WilzzLgsf4fr/psVXamxASgIE5kO+BXxL0LuNCrzijBlg8D/xHZ7QqvemhqW5pGVlthH0IClveQ/5n348DN" \
             "2ecWr/p0ORaWiwlABziR7wL/EtHlVcB5VS3Blp8Q8gfkZSmwg1f9TWpbmoAT2Q84HHgvKxVnLcASQlxoTsF0bJVhMYDOmEX4z8/LKo" \
             "QsP2VwDEFg8jIauLgkW2qLE9nOidwBfBvYnc6dn2yMjwP3O5HvOZG3JBizK5gAdECm9l+J7LanEynjWFCBSyK77exE9k9tSx1xIhOd" \
             "yJXA3cAuJU0zirCduMuJvLekOZLS81sAJzKZcA32YK/6UgnjTyBcD14nottDwNZeNWn2YieydmbLehHd/gRsWca/TSqy14xvB7YinG" \
             "KsRUiQ8ivAD/fvmAVJpxN+B7r5HmIxcKRXvbKLc0bT0yuAzPnnAh8FbnQiq6eeIwv+zIrsthlhyZ7alr8Sf+d/Y+LfFnQFJzLeiRwK" \
             "PEAouHoVcAJwGHAp4dv8eSfyLSfy5kH6/xPhhORsuuv8AGOBK5zIcV2eN4qeXQH0c/7+j3HmAR9K/W2XHR/dC2wd0e15YPPsLD+lLa" \
             "OBe4C3RXR7GRCvWpu6AE5kX0IylU1ydlkEXES4F/EmQvblfyzHuigWA+/yqr+q2pDB6MkVwBDODyHok3wl4FWXEJaZMbwemJPSjsyW" \
             "pQVsWQ04J7UtRXAi2ziRecB3yO/8AKsSVgd/JGwP6uD8EFYC38jyOtaOnhOAYZy/j7JEYC4Qm4v/k07k7SntyGy5neBAMeyXMnDlRE" \
             "ZlhVPztl/HiVxMcN4itRD6WIc0kf2UTKK805+O6KktQA7n70/y7UB2/PMA4dsoL3cSlohJ/yOcyJuABwnf7nm5F9g+W9HEzjcW+DDh" \
             "4dPWgBASkz4L/IawLbneq967Ur/RwCHA6cQFL5vIR7xq7IWtUukZAYh0/j7KEIEzgJMiu33Cq16XyoZ+tswmPkB5hFe9LGKOtxDeOR" \
             "wMbDhC8yXAl4BZXvU5J7Iz4S7ClEgbu8EfCLf9xmafcYRt26YdjPkIIdYS846kVHpCAAo6fx9JRSDb6/2OcIc8L/9NyOH/Qgob+tmy" \
             "OmEVEJPIdCEhODnsXfdseT8bOJT4Kkl/JiQ0+Uhkv7L5DnAZcM9QbzacyObAvtmniHCd6lVnFzcxLY0XgA6dH+A+YHevmiyBpxP5OK" \
             "HwZwxzvGrsyiGPLfsT/3z5Yq86aCAxW+ofBXweWLtD8+rCfGC6V70jppMTmU783v5lwr2LRyP7lUKjg4CJnH9qSufP+Drwi8g+M8u4" \
             "QupVv0lcAhOAI53IViv/MHt0tAA4j95w/icJ8YftY50fwKteBFwd2a02Jy7QYAFI6PzJn8RmAb3pxKXsWpXgWGUwnfD4Jy8D3iw4kc" \
             "lO5FbCi8NeyCv4d8Idg0le9crs6LQohxOfn/GjTuQ9HcyZjEZuAers/P1xIlcRgmMx7JFVAUpty+WEb7sYpgE7Zn/W5Wjtb4QAXdHA" \
             "4Y3AsV41JrvzsDiRTQClSycuKWncCqApzp9xEvEpuy50IrFBtTycTHCeGK4kXLutg/MvI1wF3pwgSqcQbtnlZQGwp1f9cErnB8huUJ" \
             "4d2e1txAtycholAA1z/r6UXadFdtua+EKgeWx5ihC1byJ3A+/wqp/2qk961SVe9QzgXYQTl+F4hhC03Da2PHskZxEeVsVwuhOJeUSW" \
             "nMYIQNOcvx8XEVdMBGB29sowNV8iHAs2hacI24+dsizIA8ju108BziTs6/vzJ8K//SSv+iWvGpMrIZrsbP/4yG4TqFiUGxEDaLDzA+" \
             "BE9ibsPWO41KseWYIt7wduSj1uYpYQcht8IW8Oxexewi6EL7U7verjJdo3nB13EJdv4FXC6mRBSSYNS+0FoOnO34cTuQmIycm/BNjO" \
             "q/oSbLkR2Dv1uP14kPDtuzXxGYh/ChzlVe9PbVQ3cCJTCHkKYlbXc71qJY+Xar0F6BXnz5hBXNBqDMGJymAmr10yp+BJws3ArbPrxM" \
             "cR3gHk4TFgf6+6W1OdHyDLsfjVyG5Tncg/l2HPSNRWAHrM+fGqDxL24DHsmr2LT23L70krLv3P1a/oO1f3qouADwIPD9N3EaHi8ZZe" \
             "9VsJbaqSIicu5zmR8WUYMxy1FIBec/5+zCYEtmI4t6RfjNOJK3U+FDcQvvGP96rPrfyX2UnILoTcif1XHX8lHOtt41VP9qovJrClFh" \
             "Q8cXkzcGwJ5gxL7WIAPez8ADiRQ4DLI7vN8qqxx4l5bDmY4IRFuB+YEXNpyYmsS3gxOB64P3VOxDqRvZm4D9giotuLhEdhXQtg1koA" \
             "et35Yfn7977jq7y8RPjFeCyxLaOAu4AdIrr15UD8StW32OqOE/kA8F+R3b7hVT9Whj2DUZstQBucH5an7Do6stvqxN80y2PLMsJNvz" \
             "zv0xcT4gabedUvm/OPjFe9CfhRZLcDnMi7y7BnMGqxAmiL8/fHifw7EJuTf2ev+vMSbNmH8BZ+qC+Em4CZWSDTiCDLH3A/IalIXu4B" \
             "duzwkVIuKl8BtNH5M04gLO1juLiMMuNe9fuEu+nfBl7JfvwyQRT29KofNOcvhlf9HfEVmLYDPlWCOa+h0hVAi50fACcyi/ho8SFlF5" \
             "vIMgkt9aqvjNjYGBEnsibhOvgGEd2eJGRmij1OjKIyAWi78wM4kdUIz0hj0l935RfDSIsT+TThdWUMF3jVmWXY00clWwBz/kDBByQb" \
             "EJ/o06ierwG/juzzGSeyZRnG9NF1ATDnH4hX/Q5we2S3o5xIzPmyUTEFC7aMpeR6Al0VAHP+IZlOXJnxsYTSV0aDyE5wYhO0vq+Mat" \
             "J9dE0AzPmHJiuWcUVktw84kb3KsMcolSKnP+dnVY6T0xUBMOfPxSmEKjoxnJ9dOTUaQnab88zIbpsRXpMmp/J7ADlog/P3lRk/NbLb" \
             "5sTvK43qOYdQJSiGU5zIG1Ib0hUB8Kr3AVOJfwnXCufvx5cJtQVj+LwTmViGMUY5ZPcrjovstgbxK4cR6doKoIAItM35yfLWHRPZbU" \
             "3Ce3qjQXjV7xKyH8VwoBPZKaUdXd0CRIhA65y/jyxzbWwF2YOcyPZl2GOUyjHEnf6MIlwHH5XKgK7HAHKIQGudvx/HEjLl5GU08ffN" \
             "jYopePrzduCTqWyoJAg4jAiY8wNe9f8Tf87/LidyQBn2GKXyeUJ2pBjmOJHXp5i8slOAQUTAnH8gZxDKaMdwdlae3GgIWWHaL0R225" \
             "AgHB1T6TFgPxGYhzn/ALzqC8BnI7u9EfhcCeYY5VLk9Ge6E+m4UGstEoIYg5MFe34BxER+XwHEq/6xFKOMUnAiewI/iez2I6/aUX2H" \
             "JlwEai1Zyq6jiSszPp7yyowbJeFVbyZkWI5hryzvYGFMAGpOVhPv2shu+ziR3cuwxyiVY4kv2HJBJ9fBTQCawYkUKzNeh7LeRk686k" \
             "PEn/5sQXyS2eWYADSArLjG6ZHdJhMy/hrN4gzgicg+pziRVYtMZgLQHC4EHorsc1pWjMNoCF71eeJPctYmnKZFYwLQELIqOrH54dYF" \
             "/ncJ5hjlcg1wd2SfQrkhTAAahFe9Ebg5stvhTmSbMuwxyqHg6c+bi8xlAtA8jgFejWg/hpLzyhnp8ap3At+I6FIoV4AJQI1wImOcyL" \
             "pOZJWh2nhVJb7MeGX1542OuCWi7YZFJrCbgBXhRDYhlAbbm6DeE4C1CE8+lxLeSPw5+zxCKBd1N6HM1BqEQhPrRUz5MOGGYMwrQ6NC" \
             "nMj7gB/nbL4EGBdbTmzIbxqjHJzIB4GTgHcRnH0wRgMTs8+2K/3dK8B8YCFxAtBXf96ShzSHmMdgYwg5N/8SM4FtAbqEE1nbiVxNqB" \
             "b7boZ2/pEYD7wDKFIw4iQn8saC8xrdJ/Y1aHQcwASgC2TpuxeQMJFDQV5HCXnljNJYSFzANzoOYAJQIk5klBM5D/hPYKOq7cn4mBN5" \
             "Z9VGGCOTHQfGLOlNAOpC9kDjeuIv75RN8rxyRqnEbANMAOqAE1mD8K1f1xRdOwAHVW2EkYsYAbAYQNVkZ/j/CexZtS0jMMfShzUCWw" \
             "E0jDOB91ZtRA4mArtVbYQxIjEvA00AqsSJ7Es4a28Ku1RtgDEitgVoAtn5+lUdDvMqcYUiOsUEoP7YFqAhfA4omqv9VkJml3GEs/pt" \
             "gH0JFYOvI1wBfi6BjSsTW6DS6D4xAvB6J7J6zOB2FTgB2bf/tAJdnweO86qX9/vZIsKloQWDzOOA92WfnYFCWWD6cU2H/Y3yic0OtC" \
             "Hwh7yNTQDScCLxzvgwsEdWBSgXXtUDHjgnU/pdWSEIW0TO/9/EvTYzqiFWAN5AhADYa8AEOJEnCFH1vCjB+R9PaMMmwAeyz1TCVmIo" \
             "fg18zKv+NtX8Rnk4kYWE16J52Nerfi/v2LYC6BAnsgVxzv8siZ0fwKs+AlwGXOZExgHvIYjB+wmvBl/KPj8ETvWqi1POb5TKn8kvAF" \
             "GBQBOAznlPZPvPpHb+lcnyB96afZp0LGkMzhOEwHAeoo4C7RSgc3aMaPuwV41J82QYUOJRoAlA58Qcu/xHaVYYvYwJQI2xbZRRNiYA" \
             "NSamLtvapVlh9DIxR4EWA+gyz0a03bg0K4xeJmYFsEFMrgcTgM6JqeCymxOZVJolRq8SIwCrEJEs1gSgc+6KaDsaOK4sQ4yepchtwF" \
             "yYAHTOfcDLEe2nOZHYuwNGi/GqzxEuceUldyDQBKBDvOqrhAxAeRkNXOtE1izJJKM3KeUkwAQgDbGlujYp0MdoNyYAdcWr3kHYCsRw" \
             "oBP5aBn2GD1JKUeBJgDpuKRAn69Z0U4jJ7YCqDlfAx6M7LM68D0ncnwJ9hi9hQlAncle4B0GxCZYGAWc7UR+4ESmpLfM6BFMAOpOFg" \
             "somhj0I8A9TuQ2J/Ihq9xjrITFABrCCcCTHfTfFbgB+K0TOTI2yaPRs8SsANZyIuPzNDQBSIxXfQbYD/h7h0NNIgQW/+REvuhE6lJc" \
             "1KiG2FLhubYBJgAlkG0FDk003LqElON/dCLXOpFtE41rNIvYUuG5tgEmACXhVa8BTk845FjgQOA3TmSeE9nb4gTtwasuJW5raSuAqv" \
             "GqnweOJ/5kYCR2A24EHnQih1ucoDUkPwkwASgZr3ouISYQ82AoL5sDlwKPOpHTnUh0bTijUZgANJEsT/vuwFMlTTEBOJkQJ7jGibyt" \
             "pHmMakleKNQEoEt41TuBtwO3lzjNOOATwHwnMteJ7GVxgp4iealwE4Au4lX/SNi/fwy4p+Tpdic8U1YncpgTWa3k+YzySb4FsNJgFZ" \
             "IlBpkJfIjyxfhpQrzgEq8am2HGqAFO5CPAD3I2f8yrjpiD0gSgBjiRzYBjgIMYvqZfCv4OfAO4ICs2ajQEJzITOC9n88XAql51WAc3" \
             "AagRTmQdwgWio4A3dmHKucD5wE0j/aIY1eFEtgMuIpSEj2E9r/r0cA1MAGqIExkLfBSYAWzfhSkVuBC4zquWcVxpFMCJbAicQVgZFt" \
             "kibuNVFwzXwASg5nQ5TrCQFXGCv5Q8lzEETmRVwpbwZOD1HQy1aVY1ekhMABpCFieYDhxM+XGCRayIE8SmOjM6IMsQdS7wlg6Hesar" \
             "jlhS3ASgYfSLE3wG+IcuTHkLcAHwY4sTlIcTcYRt2G6JhpznVaeO1MgEoKE4kVUIcYKZdCdO8AAr4gSvdGG+VuBE1gdOA6YBYxINuw" \
             "jYy6vOHamhCUAPkMUJZgAfpvw4wVOEOMGXLU5QnCzQexQwC1gr4dCLgX28aq5aFSYAPYQTeSsheNStOMHXCXGC+0ueq6dwInsTzvM3" \
             "Tzz0w8ARXvUneTuYAPQgTmRtVtwn6Eac4Gbg/JhfvDbiRLYixFP2TDz0C8AXCf8Hi2I6mgD0MP3iBDOAHbow5QLCL/jXLU6wAieyLj" \
             "AbOJxQvTcVy4BrgJO8amzKMMAEoDU4kV0IAcNuxAmeZEWcoJMEqY0mE+AjCM6/TuLhfw4c41V/1ckgJgAtI4sT9N0nWKPk6V5hRZxg" \
             "2BtpvYYTeR9hNSSJh34U+KxX/WaKwUwAWkoFcYKfEPaoN3dhrspwIlsQAnx7JR76JeAs4JyU17VNAFpOtkzdj7A96Eac4H5WxAmiAl" \
             "Z1JhPUWYQLWmMTDr2MsIo60as+nnBcwATA6EcWJ5gB/BPdiRNcAlzqVctKlVY6TmQMcAjhMs96iYf/JWGff2ficZdjAmC8hgriBNcT" \
             "4gQPlDxXUpzIVMJqZnLioR8HTiSskkp1UBMAY0iyZe0hhDjBiNllOmQZK+IEt5Q8V0dkAnkuoZ5jSl7Oxj3Lq76YeOxBMQEwRqRfnG" \
             "AGsGMXprwJONSrPtaFuXLjRNYkPNE9hpCANSXfAk7wqo8mHndYTACMKJzIzoSAYdlxgt8BO3nVv5Y4Ry6cyGjCdugMYGLi4X9N2Of/" \
             "38Tj5sIEwCiEE3kLIU7wKcqLE3zLq+5f0ti5yB5aXQhMSTz0E8BJwNVVPrM2ATA6womsxYr7BGXECd6bFVvtKk5kU+BswtYnJYsIgc" \
             "MvetXnE48djQmAkYQsTrAvYXuQMk4wH9g+K45ZOk5kDUIE/lhgfOLhvw8c51UfTjxuYUwAjORkcYIZhCh5ijjBYV718gTjDElWQelA" \
             "YA6wUeLh7yXs83+aeNyOMQEwSiNhnOApYJJX/VsSw1bCibyTkHY79QnHU8ApwJXdWsHEYgJglE4WJzgEOJricYILvOrMdFaBE9kYOB" \
             "M4IOW4hOIr/wc4rSzRSoUJgNE1+sUJZhAKpcawGHBe9cEEdqwOHA+cAKze6XgrcSNwrFf9feJxS8EEwKgEJ7IH4cJPTCLMH3vVD3Q4" \
             "7wGEb/3UJxYLgBl1v8W4MiYARmU4kUuAIyO77e1Vf1Rgrh0J+/x3xvYdgaeBLwCXedUliccuHRMAozKcyATg98Rly/kdoeTV4pxzbE" \
             "SI7B8IjIo2cmheJbxmnO1Vn004blcp+8mnYQxJVrjyC5HdNiecLAyLExnvRE4Gfgt8grTOfxMw2ase02TnB1sBGBWTBQbvBbaK6PYc" \
             "4Vhw0HyDTmQ/wi2+TTs2cCAPAjO96k2Jx60MWwEYleJVXyWcCsSwJiEN9gCcyBQncjvwbdI6/7OEF4CTe8n5wVYARk1wIjcQKiDnZS" \
             "mwo1e9x4lMJLzUO5i0X2pLgK8As7LtSs9hAmDUAicyiZAvMOad/c+BGwhv9NdMbNKthGO9nq56ZAJg1AYncg5wXMVmPES4yHNDxXZ0" \
             "BYsBGHXiNEKy0Cp4jnA7cOu2OD/YCsCoGU5kGnBFF6dcCnwVOKWNVYxMAIxakaXfuhvYrgvT3U54pju/C3PVEhMAo3Zk9QnKzAL0MH" \
             "C8V/1eiXM0AosBGLXDq/6MkCU3NS8Q8vCJOX8gZaliw0jJCYRKxqslGKuvjPbnvOoTCcbrGWwLYNQWJzKbUG+vE34OTPeqv05gUs9h" \
             "AmDUlixxx28pVr04aRntXsViAEZt8aovAZ+N7PYSYdWwpTn/yNgKwKg9TuRawnv+4Si1jHavYkFAowkcRCioMW2Ivy+9jHavYisAox" \
             "Fkefv3B/YAdicIwo+B/wJurrK8VpMxATCMFmNBQMNoMSYAhtFi/geHPfSDSkGregAAAABJRU5ErkJggg=="

SWIPE_ICON = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAkwAAAGoBAMAAABGd6f5AAAAMFBMVEX///8nJjYnJjYnJjYnJjYnJjYn" \
             "JjYnJjYnJjYnJjYnJjYnJjYnJjYnJjYnJjYnJjYMJptVAAAAD3RSTlMAM4i73apmIhHuzER3mVXe1sYvAAAAAWJLR0QAiAUdSAAAAA" \
             "lwSFlzAAAASAAAAEgARslrPgAADkZJREFUeNrtnc2LZFcZh6sjTje2I73IJnFhQzbuGhQh6KLRhbvQ27ia2ogEF3f+gUDjmIUDQ1Bh" \
             "FASbbIyQRc/S4MJWEJdzF0Kyu8FdVkJ6Is4w8To1Nd319d73fr0fv/ec+i2ruu4959znfpz3OVU9mWwTMDuvndT1d37i3Qzw/Oysfp" \
             "4/eDcEOlejVNc/9G4KcPavR6mu3/RuDG4eLkapfnTg3RrU3KyXc9+7OaipVoapnnq3BzN3V0ep/o93gyCzd742TFucqKzDtMWJyiZM" \
             "dX3o3Si8bMJU1194NwouFEx1XXo3Cy0UTFuc1rNLwrTFaS2v0KO0xWklO2cNw7SdAS+nCaa6fnLq3TacNMNU13/0bhxOmmHa4rQIB9" \
             "MWp+twMG1xusrXWJjq+n3vBmKk4Eepfnzg3UKE3Kjb8kvvJiKkDaYtTrO0w7TFadIFpi1O3WDa4tQJpjp7e/BSt1HK3R5UHYcpb5xu" \
             "dh2lvHHqDFPWOHWHKWucesCUsdvsA1PG9qAXTNnKqDv9RilTnGgdvsVpLXf7jlKWOPWHKUu32R+mHO3BEJgylFFDYMoPp2EwZYfTK8" \
             "NGKTOcWB3+AfdmVm6TX1vBvZuTPWBhKic7J8zbGdkDDpfZozZ3G8wHpxaYWu6D2eDUBtMWp1mWv4NJwrTFaZaiFaaWh/Spdw8swurw" \
             "8sUfsThlYQ+6wNRSJ59690E/Nzr2v8obp6Jj9/PGqStMmePUFaYWnA69+6Gbr/Y4lTicErcHfc4kdkhL755opt91mTtBk8aJg2nzxz" \
             "46PYgmGA4makabKU4cTNSElsUpWbfZFyYep2TtQV+YWr4claiMeqc3TDl+b3NQqY2tByeJ07DCbW44sTC91/gxFqcE3SYHE4dFXm6T" \
             "hYm7yOTlNofClJeMGgxTXjLq5cEw5YTTqMeffHAa9/STi9tkYfq49eO5uM32tRV88pBRrQt1WlPlgNNYmPLAaTxMWeD01miYcnCbMn" \
             "6EwykJe1CIdDB1t8nCdNF9OzKjDRuue30uvmm7ze4LddqSNE5SMKXtNuVgStptVmIwpew2ZScZycooSZjSdZv911bwSRQnDqYh1dk0" \
             "3aY0TIm6TWmY0nSb9xQOfXoySsUbpSejdA58ajixx/37OpsNiNPwtRXDtxvPHoxYWzFiw+HsgRZMackoNZgmScmoV9VgSgkn3bl8Mj" \
             "jpTuVTcZssTK+P3z6HUyB7MH5tBZ803KbE2go+RQo4acOUhtvUhykJnD416AKLU/tqToDYnBAcTiHsgc35EN1tsjAdyu0nuIziYJKc" \
             "ScR2m5JrK/iExskKptg42cEU2m0emcEU2W3aVszCyqjKEKa4MopdW/FAfn9BceJg0ji6MXGSX6jTFhanqfd4NMQapphu0x6miDLK50" \
             "LBEQyJk89tJxpOXnedYDjpra3gE8ttaq6t4MPhBGcPvGCK5Tb9YAolo/xgiuQ2fSuJYXDyrUtHcZveZWkOJyB7oL+2gk8Mt2mxtoJP" \
             "CBnlDZP/WT+6jaVNGwLg9KE7TBFwwni6g3ebBQBM+G7TaqFOW8BlFAeTZVkMW0ZZrq3gA40TCkzYOOHABO02j2BgQnabWPoHqzVLqb" \
             "COH1hzrsLq8E+w2uOIE3f0XO4tkDh5rK0Y3iI3twkHE6TbxIMJ0W3uHePBhFKvWArmHAqj+rUI6hQKDCdWhx/4DROW2/RcW8GHw8nc" \
             "HniureCD5DZxYYKSUbgwIcko1mO4azEYnGAaQgYFJ5R2NAXEbbJrK069BwnFbSKsreADMZHyX6jTFoSZFD5MEDjhw4SAE1qpgo672y" \
             "wCwOTvNmPA5C6jOJigvr9WeTYUaW0FH1ecwsDkilMcmFzd5sM4MDm6TdC1DA1xc5uOp/uQcBdSRZxYHT71HpTNOD3jcTC5rymm4oIT" \
             "4toKPi5uMxxMLm4zHkwebnPvVjyYHBwQQEFwQKwlkH89cFiMceJgenTgPRjNscUJeW0FH1O3abe24ut/+6no9izdphlMu/+cjftUsu" \
             "2G9x4rmPaq+cVOcpzsbj47VjC9/GKboisRzHCyuqveONMYeyuczG6qhcrgW7lNDqbPBfuzPKE3w0msnGi2tqJY2q7oI6tJcdpqbcVq" \
             "dUj0HlTp4+QCk/A9yAAnK5jWuxILp8VNWhmm9Z7Y4XQosIOC2b4mTIY4CXTDTOJs9kP0y+fKbpOD6algN6izQtSQqp4VZmsrKu0dqJ" \
             "4W3DGQPNj31PegiZMVTE3TCcFdaLpNK5juGuxDz21aLdRpnpteCA6TmtusnGESXhChVDbzh0n20UypbsbBJPmIzJXN8HGyWlvBKiJ8" \
             "nKxg4o6xIU4Dj7wZTNwhlsaJA3fYoceAydIeHCBssCFtMGHLKDNX2gYTNk44MCHjZLa2omgfJWC3abW2gp222+PUcwbmCdP3zjZeQn" \
             "WbjjB9QV3UMWXUriNMJXVVx3SbZgt1KJgWq5zAcTJbqPOQgom8MiK6TQ6my1PV5s4nusSlEc9tmq2tqJo2T+H0ieCORdym19qKZ/ns" \
             "xVsETmgyyhOm6Yu3qOe26YhdrUfAbTrCtCAGHidW03Qb6G5hYGp9d3RGu83R49wxd3hebvJvjw7XzQ6PhlYLdVqvPgROF4LDNNJtcq" \
             "P8WYfdd03rxafxoUooo2Yajmsr1h+0CZxKwWEaNdXgYFLW4evP2cA4AcHUOOOTygicgGBqrB+IZbDbfMkIpo4VJeKglYLDNNhtVkYw" \
             "daxPEjghyCirhToETHS1m8AJQEZxMP1esHkETHTvIXFyXFvR1PlPAXGqBnxmSDrD1GtEB2WA27SCab9P13sM6ZAMcJtWMBV9et75aj" \
             "8wve9ad5i/l4Sp52UZzG2aLdQhYOLKYGBu02qhTu8ZCJTbZGF6X7BVBEwl+wEot+m6toIPkNs0W6hz1BcmKLdpBdOgUhuMjDKDiQC8" \
             "bP0QjNu0Wqgz0CqB4GS2UIeAaar5uY7p6DbBYQJxmwhrK/p/8kKwYZ3cptXaihGXGAAZZQXTqBtWpdq0LlfnX/jBdL/zhz1xupz9Af" \
             "vMVMo1ZOTc7MgRp9mOvuwHU5+pmafbnF1B/xICJle3+fh0Mjlufltyoc6r42DylVGH7BPoVK4RAkVIAicre/CbyZea33TQ4VwccXo6" \
             "edcLpie3+27kLTecnjDTGWWY+vfQ0W1ObnnBNKCDfm6z+UYHB5On25ycNb0zlds98dOZw84WN7c5aXqj+3SrPYXUyeLmNpuGyVGHc/" \
             "HCqWmYlHV4OXBTXm5zcuIB0/BJq5PbbLjTgcLk5jbp4YOFyUtGTf6tDRNxHMoRm/Nxm+ScThIm8eqsB06XZPHyPcG9EjAdjtrgHrHF" \
             "qWCDKZyeTvY3X4QwmKabXAmB02+p6iWCDu+5zQvBJhNu85CohYPD5CCjZrXwjZ0KwkT9W9Lp+M0SOJWCw7Qxc3x+ZM/1YFK6K1njdD" \
             "h78ed6MJ1v9mcqseEjU5w+n794svLaqdzuCJh+J7Jhbbe5usj6zfmLK98vOJTbmeJ0vtDFaeWaem0rlxiW/Nqc4mxeW0YtfZt38UWo" \
             "3eOr134luC/V2hCBk+i/zX37erPfXLy4/6P5Sz8QHCXdb1Fo4zR5e34Zf/TRyqv/+m5df/uvkvtRrlsru81n6Lx2Xl9+S7DFdJTL1t" \
             "pu0yjq3VB2m0ZR74W22zSJwTmhLaMs8qH+KaHtNg2ifr+eJT5OhcX1VdttqoeASXJKfRVtt6kdAqZSYTfablM52nWO62jLKN0YwaTv" \
             "NlVD/KaYDkyxcaqsYNJ3m4rRLui37SwITsQBvkhlb3IxPr6m7ArG+mpheCUUjPnFIiROe8fmt56jgDg5PMiYPfPLhZplTbV3WoTDyW" \
             "XOblLckoxTBYjACdoeOBWAguFE/L82m3KiutsUjVtxOpTbdFQdkdwm0VbJFeZcArlNV/LjyChX8MO4TefLaBSclH8ovi1B3Kb7I14M" \
             "t1l435JDuE2qmnFq24QIMoqAqTRuQgC3CVEaw8cJAKYAbtNQh3NBd5vEYSxB2nHhPTaLMP/u2b0hQPYA55qAgjUVoEsCMk44MCG7zX" \
             "s4MIE8wFEBe/gtQHECe/Z1r1TQgZuYEzgB2AO4Mg8kToBFQ0S3CQeTe1GebBIeTIhuE9JnwLlNUDuGdvDw8H4esKMHeLGcBwsnUJjA" \
             "HlNgYcJ6TilQYYKaQkHOCq6CMyEnYHrde3SuA1PegS2AzYOCEwFT6T02SwFxm+AwoYiMh9gwTTDcJrLpAWoicahK73HBayOMDu/ZSG" \
             "OcMG4jbTlyxgnjLtIa77txDJi8n+3eiQGT87QTZr7UHgInsyIGynSpQxxxgioNtsXPbSJVBlvjVmENBZNfvT4UTG5uE8yBtcdHRmEp" \
             "sA5xOa5wfr49HgcW1mA2x+GeA2wwm2N/0wkIk4Pb3I8Ik/3sqogIk/lcHVqHc7HFiYDpY+8R6BSl/5NHx7tmOiKWVWkCptK7/11Tbb" \
             "b9QmdPgWGylFFHgWGyc5v+cjBE860Oh1ZsToYgBrM5NpdWAqapd8/7xeJGHR4meg4hvQ/iUEy9+y3Qh1J2D7tn4WEicRJebUScc1Pv" \
             "XvfPJk6Pb4vu4N2NHdz37vOAELXXUnQHG8cBWzo1ZbP4+l/R7d9a3zy2dGrKJk6yV9jjJGAicJK9hp8lAROB06Xo5hOBaRMn2WE6Tw" \
             "OmzR/Ilx2m1WvTk9vevR2eu5rDdLSy7QjSqSlrMkq2SPCNFZhOvfs6Jqs4/U90219JBaZ1nGQfL/eTgWkNp1J227dSgWnVbQpPfZcO" \
             "QXSYVsod0tWgnRMlTD1SaZ1zC5zwvjbXP9e/tKzgDObr9S8fePdRri8qfnzvx8+2+8YD7x6KZHd+2n2ks/E//8m7f2Jd+ftJ/et/dP" \
             "/7/wNfhzm8ArycagAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxNi0wNS0xOVQwMzowNjoyMyswODowMGpyZO4AAAAldEVYdGRhdGU6bW9k" \
             "aWZ5ADIwMTYtMDUtMTlUMDM6MDY6MjMrMDg6MDAbL9xSAAAAH3RFWHRwczpIaVJlc0JvdW5kaW5nQm94ADU4OHg0MjQrMCswngLBEw" \
             "AAABx0RVh0cHM6TGV2ZWwAQWRvYmUtMy4wIEVQU0YtMy4wCptwu+MAAAAASUVORK5CYII="


def click_marker(im: Image, *args) -> bytes:
    """为点击添加水印"""
    byte_data = base64.b64decode(CLICK_ICON.replace('data:image/png;base64,', ''))
    mark = Image.open(BytesIO(byte_data))  # 加载图标

    mark_size = int(im.size[0] * MARKER_RESIZE)
    mark = mark.resize((mark_size, mark_size), Image.ANTIALIAS)  # 动态图标缩放，保证任意分辨率都能看清

    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))

    # 水印图标的"小手"不是指向左上角的，打完水印会偏离较远————适当修正能以免造成困扰
    fix = (int(args[0] - mark_size * MARKER_OFFSET_X), int(args[1] - mark_size * MARKER_OFFSET_Y))
    layer.paste(mark, fix)

    out = Image.composite(layer, im, layer)
    output_buffer = BytesIO()
    out.save(output_buffer, format='JPEG')
    return output_buffer.getvalue()


def swipe_marker(im: Image, *args):
    """为滑动添加水印"""
    draw = ImageDraw.Draw(im)
    draw.line([i for i in args[:4]], fill='#ff0000', width=10)
    output_buffer = BytesIO()
    im.save(output_buffer, format='JPEG')
    return output_buffer.getvalue()
