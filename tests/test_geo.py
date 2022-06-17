from unittest.mock import patch, MagicMock


def test_compare_geolocation():
    import numpy as np
    import fcitools.geo
    sc = MagicMock()
    sc["vis_09"].area.x_size = 5
    sc["vis_09"].area.y_size = 5
    sc["vis_09"].area.resolution = (1000, 1000)

    lon1 = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
    lat1 = np.array([[8, 7, 6], [5, 4, 3], [2, 1, 0]])

    lon2 = np.array([[0, 1, 2], [4, 5, 6], [6, 7, 8]])
    lat2 = np.array([[9, 8, 7], [5, 4, 3], [2, 1, 0]])

    sc["vis_09"].area.get_lonlats.return_value = (lon1, lat1)

    fs = MagicMock()
    with patch.dict("sys.modules", {"fcitools.eumsecret": fs}):
        fs.pixcoord2geocoord.return_value = (lat2, lon2)
        rgb1 = fcitools.geo.compare_geolocation(sc, "vis_09")
        fs.pixcoord2geocoord.return_value = (lat1, lon1)
        rgb2 = fcitools.geo.compare_geolocation(sc, "vis_09")

    np.testing.assert_allclose(
            rgb1,
            np.array([[[1, 0, 0], [1, 0, 0], [1, 0, 0]],
                      [[0.5, 1, 0], [0.5, 1, 0], [0.5, 1, 0]],
                      [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]),
            rtol=0.01)

    np.testing.assert_allclose(rgb2, np.zeros(shape=(3, 3, 3)))
