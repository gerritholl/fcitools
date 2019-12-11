from unittest.mock import patch, MagicMock


def test_calc_heading_distance_accurate():
    # just a thin wrapper around pyproj
    import dask.array.core
    import dask.array
    from fcitools.geo import calc_heading_distance_accurate
    from pyproj.geod import Geod
    import numpy as np
    lat1 = np.array([[1, 2], [3, 4]])
    lon1 = np.array([[1, 2], [3, 4]])
    dlat1 = dask.array.from_array(lat1)
    dlon1 = dask.array.from_array(lon1)
    lat2 = lat1 + 0.5
    lon2 = lon1 + 0.5
    dlat2 = dlat1 + 0.5
    dlon2 = dlon1 + 0.5
    (hr, _, dr) = Geod(ellps="WGS84").inv(lon1, lat1, lon2, lat2)
    (hhn, dhn) = calc_heading_distance_accurate(lon1, lat1, lon2, lat2)
    (hhd, dhd) = calc_heading_distance_accurate(dlon1, dlat1, dlon2, dlat2)
    assert isinstance(hhd, dask.array.core.Array)
    np.testing.assert_allclose(hhn, hr)
    np.testing.assert_allclose(dhn, dr)
    np.testing.assert_allclose(hhd, hr)
    np.testing.assert_allclose(dhd, dr)


def test_rgb_from_heading_distance():
    from fcitools.geo import calc_rgb_from_heading_distance
    import numpy as np
    h = [-120, -60, 0, 60, 120, 180]
    d = np.array([0, 250, 500, 1000])
    (hm, dm) = np.meshgrid(h, d)
    rgb = calc_rgb_from_heading_distance(hm, dm, f=1/1000)
    # all black at zero distance
    assert (rgb[0, :, :] == 0).all()
    # fully saturated at 1000 metre distance
    # test main colours
    np.testing.assert_array_equal(rgb[3, 0, :], [1, 1, 0])
    np.testing.assert_array_equal(rgb[3, 1, :], [0, 1, 0])
    np.testing.assert_array_equal(rgb[3, 2, :], [0, 1, 1])
    np.testing.assert_array_equal(rgb[3, 3, :], [0, 0, 1])
    np.testing.assert_array_equal(rgb[3, 4, :], [1, 0, 1])
    np.testing.assert_array_equal(rgb[3, 5, :], [1, 0, 0])


def test_get_legend():
    from fcitools.geo import get_legend
    import numpy as np

    n = 361
    rgb = get_legend(n, (-180, 180), (0, 100))
    assert rgb.shape == (n, n, 3)
    assert (rgb[0, :, :] == 0).all()
    np.testing.assert_array_equal(rgb[-1, 0, :], [1, 0, 0])
    np.testing.assert_array_equal(rgb[-1, 60, :], [1, 1, 0])
    np.testing.assert_array_equal(rgb[-1, 120, :], [0, 1, 0])
    np.testing.assert_array_equal(rgb[-1, 180, :], [0, 1, 1])
    np.testing.assert_array_equal(rgb[-1, 240, :], [0, 0, 1])
    np.testing.assert_array_equal(rgb[-1, 300, :], [1, 0, 1])


def test_plot_legend():
    from fcitools.geo import plot_legend
    import numpy as np
    leg = np.arange(25).reshape(5, 5)
    ang_range = (-180, 180)
    dist_range = (0, 10)
    (f, a) = plot_legend(leg, ang_range, dist_range)
    assert a.get_xlim() == ang_range
    assert a.get_ylim() == dist_range
    assert a.get_aspect() == "auto"
    assert f.axes == [a]
    assert a.get_xlabel() == "direction / degrees"
    assert a.get_ylabel() == "distance / m"


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


@patch("PIL.Image")
def test_save_rgb(pi):
    import numpy as np
    from fcitools.geo import save_rgb
    rgb = np.linspace(0, 1, 5 * 5 * 3).reshape(5, 5, 3)
    save_rgb(rgb, "/dev/null")
    pi.fromarray.return_value.save.assert_called_once_with("/dev/null")
