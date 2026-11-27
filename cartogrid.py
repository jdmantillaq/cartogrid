# %%
import cartopy.crs as ccrs
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd


def add_map_features(ax, lon_step=30, lat_step=15, map_resolution=50,
                     countries=False, coastline=True, rivers=False,
                     projection=None, fontsize_latlon=10, number_format='.0f',
                     **kwargs):
    """
    Add continents, coastlines, gridlines, and tick labels to a Cartopy axes.
    Custom colors can also be set for shapes and countries.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxesSubplot
        The Cartopy axes to modify.
    lon_step : int, optional
        The step size for longitude gridlines and tick labels, by default 30.
    lat_step : int, optional
        The step size for latitude gridlines and tick labels, by default 15.
    map_resolution : str, optional
        Resolution of the coastlines, by default '50'.
    countries : bool, optional
        If True, adds high-resolution country borders to the axes,
        by default True.
    rivers : bool, optional
        If True, adds the representation of rivers to the axes,
        by default False.
    **kwargs
        color_shape: str, optional
            The color of the shape borders, by default 'k' (black).
        color_country: str, optional
            The color of the country borders, by default 'k' (black).

    Returns
    -------
    cartopy.mpl.geoaxes.GeoAxesSubplot
        The modified Cartopy axes with the added features and gridlines.
    """

    import numpy as np
    import cartopy.crs as ccrs
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    import cartopy.feature as cfeature

    # Use the projection currently attached to the axis if none is provided
    if projection is None:
        projection = ax.projection

    # Extract central longitude if available
    central_lon = getattr(projection, 'central_longitude', 0)

    # -----------------------------------------
    # UNIVERSAL LONGITUDE GRID GENERATION
    # -----------------------------------------

    # Create tick values centered on the projection’s central longitude
    lon_min = central_lon - 180
    lon_max = central_lon + 180
    lon_val = np.arange(lon_min, lon_max + lon_step, lon_step)

    # Normalize to [-180, 180] for proper formatting
    lon_val = ((lon_val + 180) % 360) - 180

    # -----------------------------------------
    # TICKS, LABELS, GRID
    # -----------------------------------------

    ax.set_xticks(lon_val, crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, lat_step), crs=ccrs.PlateCarree())

    # fontsize_latlon = kwargs.get('fontsize_latlon', 12)
    ax.tick_params(axis='both', labelsize=fontsize_latlon, color="#434343")

    # LongitudeFormatter interprets values as degrees east of Greenwich
    lon_formatter = LongitudeFormatter(number_format=number_format,
                                       zero_direction_label=True)
    lat_formatter = LatitudeFormatter()

    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.set_axisbelow(False)

    # GRIDLINES
    ax.grid(which='major', linestyle='--', linewidth=0.6,
            color='gray', alpha=0.8, zorder=9)

    # -----------------------------------------
    # FEATURES (coastlines, borders, rivers)
    # -----------------------------------------

    lw_coastlines = kwargs.get('lw_coastlines', 0.8)
    color_country = kwargs.get('color_country', 'k')
    lw_country = kwargs.get('lw_country', 1)
    color_river = kwargs.get('color_river', 'gray')
    lw_river = kwargs.get('lw_river', 0.6)

    if coastline:
        ax.coastlines(resolution=f"{map_resolution}m",
                      color='k', lw=lw_coastlines, zorder=10)

    if countries:
        borders = cfeature.NaturalEarthFeature(
            'cultural', 'admin_0_boundary_lines_land',
            scale=f"{map_resolution}m", facecolor='none')
        ax.add_feature(borders, edgecolor=color_country,
                       lw=lw_country, zorder=11)

    if rivers:
        rivers_feat = cfeature.NaturalEarthFeature(
            'physical', 'rivers_lake_centerlines',
            scale=f"{map_resolution}m", facecolor='none')
        ax.add_feature(rivers_feat, edgecolor=color_river,
                       lw=lw_river, zorder=11)

    return ax


def format_longitude_axis(ax, lon_values, lon_step=30, number_format='.0f'):
    """Format x-axis with longitude labels.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to format.
    lon_values : array-like
        Longitude values to determine tick range.
    lon_step : float, optional
        Step between longitude ticks (default: 20).

    Returns
    -------
    ax : matplotlib.axes.Axes
        The formatted axes.
    """
    from cartopy.mpl.ticker import LongitudeFormatter
    lon_formatter = LongitudeFormatter(number_format=number_format,
                                       zero_direction_label=True,
                                       )
    lon_min = np.min(lon_values)
    lon_max = np.max(lon_values)

    # Round to nearest lon_step for cleaner ticks
    lon_min_tick = np.ceil(lon_min / lon_step) * lon_step
    lon_max_tick = np.floor(lon_max / lon_step) * lon_step
    lon_ticks = np.arange(lon_min_tick, lon_max_tick + lon_step, lon_step)

    # Handle both -180 to 180 and 0 to 360 conventions
    if lon_min >= 0 and lon_max > 180:
        # 0 to 360 convention: convert ticks > 180 for formatter
        # LongitudeFormatter expects -180 to 180, so we need custom labels
        ax.set_xticks(lon_ticks)
        labels = []
        for lon in lon_ticks:
            if lon == 0 or lon == 360:
                labels.append('0°')
            elif lon == 180:
                labels.append('180°')
            elif lon > 180:
                labels.append(f'{int(360 - lon)}°W')
            else:
                labels.append(f'{int(lon)}°E')
        ax.set_xticklabels(labels)
    else:
        # -180 to 180 convention: use LongitudeFormatter directly
        ax.set_xticks(lon_ticks)
        ax.xaxis.set_major_formatter(lon_formatter)

    return ax


def define_grid_fig(num_rows, num_columns,
                    horiz_spacing=0.015, vert_spacing=0.05,
                    undermap=False, map_height_ratio=0.30,
                    map_vert_coord=None, **kwargs):
    """Calculate subplot positions with an optional shorter map row.

    Parameters
    ----------
    num_rows, num_columns : int
        Number of regular subplot rows and columns.
    horiz_spacing : float
        Horizontal spacing between columns.
    vert_spacing : float
        Vertical spacing between regular subplot rows.
    undermap : bool
        If True, add an additional bottom row for maps.
    map_height_ratio : float
        Height of the map row relative to regular subplots.
    map_vert_spacing : float or None
        Vertical spacing between the last regular subplot row
        and the map row.

        Positive values create a gap.
        Zero places the rows directly adjacent.
        Negative values allow vertical overlap.

        If None, defaults to vert_spacing.

    Returns
    -------
    x_coords, y_coords, x_fig, y_fig
        Subplot coordinates and regular subplot dimensions.
        The map height is y_fig * map_height_ratio.
    """

    if num_rows < 1 or num_columns < 1:
        raise ValueError("num_rows and num_columns must be positive")

    if undermap and map_height_ratio <= 0:
        raise ValueError("map_height_ratio must be positive")

    if map_vert_coord is None:
        map_vert_coord = -0.05

    left_border = kwargs.get('left_border', 0.01)
    right_border = kwargs.get('right_border', 0.03)
    top_border = kwargs.get('top_border', 0.03)
    bottom_border = kwargs.get('bottom_border', 0.03)

    # Horizontal coordinates
    x_fig = (
        1 - left_border - right_border
        - (num_columns - 1) * horiz_spacing
    ) / num_columns

    x_corner = kwargs.get('x_corner',
                          lambda i: left_border + i * (x_fig + horiz_spacing))

    x_coords = [x_corner(i) for i in range(num_columns)]

    # Vertical dimensions
    regular_gaps = (num_rows - 1) * vert_spacing
    # map_gap = map_vert_spacing if undermap else 0

    available_height = (1 - top_border - bottom_border - regular_gaps)

    height_units = num_rows + (map_height_ratio if undermap else 0)

    y_fig = available_height / height_units

    if x_fig <= 0 or y_fig <= 0:
        raise ValueError("Borders or spacing leave no room for subplots")

    y_coords = [bottom_border + (num_rows - 1 - i) * (y_fig + vert_spacing)
                for i in range(num_rows)]

    if undermap:
        y_coords.append(map_vert_coord)

    y_coords = np.array(y_coords)

    return x_coords, y_coords, x_fig, y_fig


def add_colorbar(fig, cs, label, orientation, grid_prop,
                 cbar_factor=0.8, cbar_width=0.025, fontsize=12, **kwargs):
    """
    Add a colorbar to a figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to which the colorbar will be added.
    cs : QuadContourSet
        The contour plot for which the colorbar will be created.
    label : str
        The label for the colorbar.
    orientation : str
        The orientation of the colorbar, either 'horizontal' or 'vertical'.
    grid_prop : tuple
        Tuple containing the x-coordinates, y-coordinates, width,
        and height of each subplot.
    cbar_factor : float, optional
        The scaling factor for the colorbar, by default 0.8.
        Determines the length of the colorbar relative to the plot.
    cbar_width : float, optional
        The width of the colorbar, by default 0.025.
    **kwargs : dict, optional
        Additional keyword arguments for customizing the position of the
        colorbar. Can include 'y_coord_cbar' and 'x_coord_cbar' for vertical
        and horizontal colorbars respectively.

    Raises
    ------
    ValueError
        If the orientation is neither 'horizontal' nor 'vertical'.
    """

    # Unpack the properties of the grid
    (x_coords, y_coords, x_fig, y_fig) = grid_prop

    # Get the y-coordinate for the colorbar, default to -0.1 if not specified
    y_coord_cbar = kwargs.get('y_coord_cbar', -0.1)

    # Get the x-coordinate for the colorbar, default to 1 if not specified
    x_coord_cbar = kwargs.get('x_coord_cbar', 1)

    extend = kwargs.get('extend', 'both')
    ticks = kwargs.get('ticks', None)

    # Check the orientation of the colorbar
    if orientation == 'horizontal':
        # Calculate the axes of the colorbar for a horizontal orientation
        cbaxes = fig.add_axes([
            x_coords[0] + (1-cbar_factor)*(x_coords[-1]+x_fig-x_coords[0])/2,
            y_coord_cbar,
            (x_coords[-1]+x_fig-x_coords[0])*cbar_factor,
            cbar_width])

        if ticks is not None:
            # Add a horizontal colorbar to the figure with specified ticks
            cbar = fig.colorbar(cs, cax=cbaxes, orientation='horizontal',
                                extend=extend, label=label, ticks=ticks)
        else:
            # Add a horizontal colorbar to the figure
            cbar = fig.colorbar(cs, cax=cbaxes, orientation='horizontal',
                                extend=extend, label=label)
        cbar.ax.tick_params(labelsize=fontsize)
        cbar.set_label(label, fontsize=fontsize)

    elif orientation == 'vertical':
        # Calculate the axes of the colorbar for a vertical orientation
        cbaxes = fig.add_axes([x_coord_cbar,
                               y_coords[-1] + (1-cbar_factor) *
                               (y_coords[0]+y_fig-y_coords[-1])/2,
                               cbar_width,
                               (y_coords[0]+y_fig-y_coords[-1])*cbar_factor])

        # Add a vertical colorbar to the figure
        if ticks is not None:
            cbar = fig.colorbar(cs, cax=cbaxes, label=label, extend=extend,
                                ticks=ticks)
        else:
            cbar = fig.colorbar(cs, cax=cbaxes, label=label, extend=extend,)
        cbar.ax.tick_params(labelsize=fontsize)
        cbar.set_label(label, fontsize=fontsize)

    else:
        # Raise an error if the orientation is not recognized
        raise ValueError(
            "Invalid orientation. Choose either 'horizontal' or 'vertical'.")


def _resolve_index_span(idx, n_items, name='idx'):
    """
    Convert a single index or a ``[start, end]`` pair into an inclusive
    ``(start, end)`` tuple of non-negative indices.

    Parameters
    ----------
    idx : int or sequence of int
        A single index (e.g. ``2``) or a sequence ``[start, end]``
        (e.g. ``[1, 3]`` -> elements 1, 2 and 3). Negative indices are
        allowed and follow Python conventions.
    n_items : int
        Number of available elements.
    name : str, optional
        Name of the argument, used in error messages.

    Returns
    -------
    tuple of int
        ``(start, end)`` with ``start <= end``.
    """
    if np.isscalar(idx):
        start = end = int(idx)
    else:
        idx = list(idx)
        if len(idx) == 1:
            start = end = int(idx[0])
        elif len(idx) == 2:
            start, end = int(idx[0]), int(idx[1])
        else:
            raise ValueError(
                f"{name} must be an int or a [start, end] pair, got {idx}")

    # Normalize negative indices
    start = start + n_items if start < 0 else start
    end = end + n_items if end < 0 else end

    for i in (start, end):
        if not 0 <= i < n_items:
            raise IndexError(
                f"{name} value {i} out of range for {n_items} elements")

    return min(start, end), max(start, end)


def add_colorbar_col(fig, cs, label, grid_prop, col_idx,
                     cbar_factor=0.8, cbar_width=0.025, fontsize=12,
                     y_coord_cbar=-0.1, **kwargs):
    """
    Add a horizontal colorbar under one column or a span of columns.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to which the colorbar will be added.
    cs : QuadContourSet
        The contour plot for which the colorbar will be created.
    label : str
        The label for the colorbar.
    col_idx : int or sequence of int
        Column index where the colorbar is placed. Either a single index
        (e.g. ``1``) or an inclusive ``[start, end]`` pair (e.g. ``[1, 3]``
        spans columns 1, 2 and 3).
    grid_prop : tuple
        Tuple containing the x-coordinates, y-coordinates, width,
        and height of each subplot.
    cbar_factor : float, optional
        The scaling factor for the colorbar, by default 0.8.
        Determines the length of the colorbar relative to the plot.
    cbar_width : float, optional
        The width of the colorbar, by default 0.025.
    **kwargs : dict, optional
        Additional keyword arguments for customizing the position of the
        colorbar. Can include 'y_coord_cbar' and 'x_coord_cbar' for vertical
        and horizontal colorbars respectively.

    Raises
    ------
    ValueError
        If the orientation is neither 'horizontal' nor 'vertical'.
    """

    # Unpack the properties of the grid
    (x_coords, y_coords, x_fig, y_fig) = grid_prop

    # Get the y-coordinate for the colorbar, default to -0.1 if not specified
    # y_coord_cbar = kwargs.get('y_coord_cbar', -0.1)

    # Get the x-coordinate for the colorbar, default to 1 if not specified
    # x_coord_cbar = kwargs.get('x_coord_cbar', 1)

    extend = kwargs.get('extend', 'both')
    ticks = kwargs.get('ticks', None)

    # Resolve the column span (inclusive)
    col_start, col_end = _resolve_index_span(col_idx, len(x_coords),
                                             name='col_idx')
    x_left = x_coords[col_start]
    span_width = x_coords[col_end] + x_fig - x_left

    # Calculate the axes of the colorbar for a horizontal orientation
    cbaxes = fig.add_axes([
        x_left + (1-cbar_factor)*span_width/2,
        y_coord_cbar,
        span_width*cbar_factor,
        cbar_width])

    # Add a horizontal colorbar to the figure
    if ticks is not None:
        cbar = fig.colorbar(cs, cax=cbaxes, orientation='horizontal',
                            label=label, extend=extend, ticks=ticks)
    else:
        cbar = fig.colorbar(cs, cax=cbaxes, orientation='horizontal',
                            extend=extend, label=label)
    cbar.ax.tick_params(labelsize=fontsize)
    cbar.set_label(label, fontsize=fontsize)


def add_colorbar_row(fig, cs, label, grid_prop, row_idx,
                     cbar_factor=0.8, cbar_width=0.025, fontsize=12, **kwargs):
    """
    Add a colorbar to a figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to which the colorbar will be added.
    cs : QuadContourSet
        The contour plot for which the colorbar will be created.
    label : str
        The label for the colorbar.
    orientation : str
        The orientation of the colorbar, either 'horizontal' or 'vertical'.
    grid_prop : tuple
        Tuple containing the x-coordinates, y-coordinates, width,
        and height of each subplot.
    cbar_factor : float, optional
        The scaling factor for the colorbar, by default 0.8.
        Determines the length of the colorbar relative to the plot.
    cbar_width : float, optional
        The width of the colorbar, by default 0.025.
    **kwargs : dict, optional
        Additional keyword arguments for customizing the position of the
        colorbar. Can include 'y_coord_cbar' and 'x_coord_cbar' for vertical
        and horizontal colorbars respectively.

    Raises
    ------
    ValueError
        If the orientation is neither 'horizontal' nor 'vertical'.
    """

    # Unpack the properties of the grid
    (x_coords, y_coords, x_fig, y_fig) = grid_prop

    # Get the y-coordinate for the colorbar, default to -0.1 if not specified
    y_coord_cbar = kwargs.get('y_coord_cbar', -0.1)

    # Get the x-coordinate for the colorbar, default to 1 if not specified
    x_coord_cbar = kwargs.get('x_coord_cbar', 1)

    extend = kwargs.get('extend', 'both')
    ticks = kwargs.get('ticks', None)

    # Resolve the row span (inclusive). Rows are ordered top to bottom,
    # so the bottom edge comes from the last row of the span.
    row_start, row_end = _resolve_index_span(row_idx, len(y_coords),
                                             name='row_idx')
    y_bottom = min(y_coords[row_start], y_coords[row_end])
    span_height = max(y_coords[row_start],
                      y_coords[row_end]) + y_fig - y_bottom

    # Calculate the axes of the colorbar for a vertical orientation
    cbaxes = fig.add_axes([x_coord_cbar,
                           y_bottom + (1-cbar_factor)*span_height/2,
                           cbar_width,
                           span_height*cbar_factor])

    # Add a vertical colorbar to the figure
    if ticks is not None:
        cbar = fig.colorbar(cs, cax=cbaxes, label=label,
                            extend=extend, ticks=ticks)
    else:
        cbar = fig.colorbar(cs, cax=cbaxes, label=label, extend=extend)
    cbar.ax.tick_params(labelsize=fontsize)
    cbar.set_label(label, fontsize=fontsize)


# -----------------------------------------------------------------------------
# Hovmöller panels with aligned geographic reference maps
# -----------------------------------------------------------------------------
def add_hovmoller_reference_map(ax, lat_band=None, lat_extent=(-20, 20),
                                lon_extent=(0, 360), lon_step=60,
                                band_color='tab:purple', band_alpha=0.25,
                                band_lines=True, coastlines=True,
                                land_color='0.88', gridlines=True,
                                fontsize=9, map_resolution='110m'):
    """Style an existing Cartopy GeoAxes as a tropical longitude reference map.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxes
        Existing map axis (typically from ``make_hovmoller_map_grid``).
    lat_band : tuple(float, float) or None
        Southern and northern boundaries of the latitude-averaging region.
        If None, no band is drawn. Order is immaterial.
    lat_extent, lon_extent : tuple(float, float)
        Visible map bounds, in geographic degrees.
    lon_step : float
        Spacing of geographic longitude ticks.

    Returns
    -------
    ax : cartopy.mpl.geoaxes.GeoAxes
    """
    import cartopy.feature as cfeature
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    from matplotlib.patches import Rectangle

    south, north = sorted(map(float, lat_extent))
    west, east = map(float, lon_extent)
    if not south < north or not west < east:
        raise ValueError('lat_extent and lon_extent must have distinct bounds')
    if lon_step <= 0:
        raise ValueError('lon_step must be positive')

    geo = ccrs.PlateCarree()
    ax.set_extent([west, east, south, north], crs=geo)
    if land_color is not None:
        ax.add_feature(cfeature.LAND, facecolor=land_color, edgecolor='none',
                       zorder=1)
    if coastlines:
        ax.coastlines(resolution=map_resolution, linewidth=0.7,
                      color='0.3', zorder=3)

    if lat_band is not None:
        band_s, band_n = sorted(map(float, lat_band))
        if not -90 <= band_s < band_n <= 90:
            raise ValueError(
                'lat_band must specify two latitudes in [-90, 90]')
        # Split at the 180-degree seam to avoid a polygon crossing the globe.
        breaks = [west] + [180 + 360*k for k in range(-2, 4)
                           if west < 180 + 360*k < east] + [east]
        for left, right in zip(breaks[:-1], breaks[1:]):
            ax.add_patch(Rectangle((left, band_s), right-left, band_n-band_s,
                                   transform=geo, facecolor=band_color,
                                   alpha=band_alpha, edgecolor='none', zorder=4))
            if band_lines:
                for lat in (band_s, band_n):
                    ax.plot([left, right], [lat, lat], transform=geo,
                            color=band_color, linestyle='--', linewidth=1,
                            zorder=5)

    ticks = np.arange(np.ceil(west / lon_step) * lon_step,
                      east + 1e-8, lon_step)
    # Cartopy can reject longitude ticks on a shifted projection; use the
    # geographic CRS explicitly and rely on the GeoAxes formatter.
    ax.set_xticks(ticks, crs=geo)
    ax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
    lat_ticks = np.array([south, 0., north])
    ax.set_yticks(np.unique(lat_ticks), crs=geo)
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.tick_params(labelsize=fontsize, length=2)
    if gridlines:
        ax.gridlines(crs=geo, draw_labels=False, linewidth=0.5,
                     color='0.5', alpha=0.5, linestyle=':')
    # Prevent Cartopy's default equal aspect from shrinking the map horizontally.
    ax.set_aspect('auto')
    return ax


def add_hovmoller_reference_map(ax, lat_band=None, lat_extent=(-20, 20),
                                lon_extent=(0, 360), lat_step=10, lon_step=60,
                                central_longitude=None,
                                band_color='tab:purple',
                                band_alpha=0.25,
                                band_lines=True,
                                coastlines=True,
                                land_color='0.88',
                                gridlines=True,
                                fontsize=9,
                                map_resolution='110m',
                                ):
    """Add a geographic reference map beneath a Hovmöller diagram.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxes
        Existing Cartopy geographic axes.
    lat_band : tuple, optional
        Latitude range used for meridional averaging.
    lat_extent, lon_extent : tuple
        Geographic map boundaries in degrees.
    lon_step, lat_step : float
        Longitude and latitude tick intervals.
    central_longitude : float, optional
        Central longitude of the map projection. If None,
        inferred from the existing axes projection.
    band_color : str
        Color of the latitude averaging band.
    band_alpha : float
        Transparency of the averaging band.
    band_lines : bool
        Whether to draw dashed lines at the band boundaries.
    coastlines : bool
        Whether to draw coastlines.
    land_color : str
        Color of land areas.
    gridlines : bool
        Whether to display geographic gridlines.
    fontsize : int
        Font size of longitude and latitude labels.
    map_resolution : str
        Natural Earth resolution ('110m', '50m', '10m').

    Returns
    -------
    ax : cartopy.mpl.geoaxes.GeoAxes
        Modified geographic axes.
    """

    import numpy as np
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from cartopy.mpl.ticker import (
        LongitudeFormatter,
        LatitudeFormatter,
    )

    data_crs = ccrs.PlateCarree()

    # Read projection central longitude
    projection_central_lon = getattr(ax.projection, 'central_longitude',
                                     None)

    if projection_central_lon is None:
        projection_central_lon = getattr(ax.projection, 'proj4_params',
                                         {},).get('lon_0', 0)

    if central_longitude is None:
        central_longitude = projection_central_lon

    # The axes projection must be established when creating ax.
    if not np.isclose((central_longitude - projection_central_lon) % 360,
                      0, atol=1e-8,) \
        and not np.isclose((projection_central_lon - central_longitude) % 360,
                           0, atol=1e-8):
        raise ValueError(
            "central_longitude must match the existing axes "
            "projection. Create the axes with "
            "ccrs.PlateCarree(central_longitude=...)."
        )

    # Geographic extent
    ax.set_extent([lon_extent[0], lon_extent[1], lat_extent[0], lat_extent[1],],
                  crs=data_crs)

    # Geographic features
    ax.add_feature(cfeature.LAND, facecolor=land_color, edgecolor='none',
                   zorder=1)

    if coastlines:
        ax.coastlines(resolution=map_resolution, linewidth=0.8, color='0.25',
                      zorder=3)

    # Latitude averaging band
    if lat_band is not None:
        lat_south, lat_north = sorted(lat_band)

        ax.axhspan(lat_south, lat_north, transform=data_crs, color=band_color,
                   alpha=band_alpha, zorder=4)

        if band_lines:
            for latitude in (lat_south, lat_north):
                ax.plot([lon_extent[0], lon_extent[1]], [latitude, latitude],
                        transform=data_crs, color=band_color, linestyle='--',
                        linewidth=1.1, zorder=5)

    # Longitude and latitude ticks
    lon_ticks = np.arange(np.ceil(lon_extent[0] / lon_step) * lon_step,
                          lon_extent[1] + 1e-8, lon_step)

    lat_ticks = np.arange(np.ceil(lat_extent[0] / lat_step) * lat_step,
                          lat_extent[1] + 1e-8, lat_step)

    ax.set_xticks(lon_ticks, crs=data_crs)
    ax.set_yticks(lat_ticks, crs=data_crs)

    ax.xaxis.set_major_formatter(LongitudeFormatter(
        zero_direction_label=True, dateline_direction_label=True))
    ax.yaxis.set_major_formatter(LatitudeFormatter())

    ax.tick_params(axis='both', labelsize=fontsize)

    if gridlines:
        ax.grid(which='major', linewidth=0.6, color='0.6', alpha=0.6,
                linestyle=':')
    ax.set_aspect('auto')
    return ax


def format_hovmoller_longitude_axis(
    ax, lon_values=None, lon_extent=None, lon_step=60,
    central_longitude=180, tick_fontsize=9, show_labels=True,
    show_grid=False, number_format='.0f',
):
    """Format a regular Hovmöller x-axis as geographic longitudes.

    Tick *positions* remain in the longitude coordinate system of the data.
    ``central_longitude`` identifies the associated map projection, but does
    not reproject or roll the Hovmöller data. For exact alignment with a map,
    both panels must have the same left-to-right geographic longitude order.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Hovmöller axis (not a Cartopy GeoAxes).
    lon_values : array-like, optional
        Longitudes of the plotted field. Used to infer bounds when
        ``lon_extent`` is omitted.
    lon_extent : tuple, optional
        Explicit left and right longitude limits in the field's coordinates.
    lon_step : float
        Longitude tick interval, in degrees.
    central_longitude : float
        Central longitude of the accompanying map (informational only).
    tick_fontsize : float
        Longitude tick-label font size.
    show_labels : bool
        Whether to show longitude tick labels.
    show_grid : bool
        Whether to draw vertical grid lines at longitude ticks.
    number_format : str
        Format specification for numeric longitude values.

    Returns
    -------
    matplotlib.axes.Axes
    """
    from matplotlib.ticker import FuncFormatter

    if lon_step <= 0:
        raise ValueError('lon_step must be positive')
    if not np.isfinite(central_longitude):
        raise ValueError('central_longitude must be finite')

    if lon_extent is None:
        if lon_values is None:
            lon_extent = ax.get_xlim()
        else:
            values = np.asarray(lon_values, dtype=float)
            values = values[np.isfinite(values)]
            if values.size == 0:
                raise ValueError('lon_values must contain finite values')
            lon_extent = (values.min(), values.max())

    west, east = map(float, lon_extent)
    if not np.isfinite([west, east]).all() or west >= east:
        raise ValueError('lon_extent must contain increasing finite bounds')

    ticks = np.arange(np.ceil(west / lon_step) * lon_step,
                      east + lon_step * 1e-8, lon_step)

    def longitude_label(value, _pos):
        # Wrap only the label, never the tick position.
        longitude = value % 360
        if np.isclose(longitude, 0) or np.isclose(longitude, 360):
            return '0°'
        if np.isclose(longitude, 180):
            return '180°'
        if longitude < 180:
            return f'{longitude:{number_format}}°E'
        return f'{360 - longitude:{number_format}}°W'

    ax.set_xlim(west, east)
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(FuncFormatter(longitude_label))
    ax.tick_params(axis='x', which='major', labelsize=tick_fontsize,
                   labelbottom=show_labels)
    # ax.grid(axis='x', visible=show_grid, which='major',
    #         linestyle=':', linewidth=0.6, alpha=0.5)
    return ax


if __name__ == '__main__':

    # Define the map projection (PlateCarree) and set the image extent
    projection = ccrs.PlateCarree(central_longitude=0)

    img_extent = (0, 120, -30, 30)

    # Define the grid size (number of rows and columns)
    num_rows = 4
    num_columns = 4

    # Create a figure with a specified size
    fig = plt.figure(figsize=(8, 4))

    y_map = 0.13
    # Use the function to calculate properties of the grid

    cs = None  # Placeholder for the contour set, replace with actual data

    # Use the function to calculate properties of the grid
    x_coords, y_coords, x_fig, y_fig = define_grid_fig(
        num_rows, num_columns,
        undermap=True, map_vert_coord=-0.2
    )

    # Define font properties for axis labels and title
    font_prop = {'fontsize': 12, 'fontweight': 'semibold', 'color': '#434343'}
    font_prop_title = {'fontsize': 14,
                       'fontweight': 'semibold', 'color': '#434343'}

    # Initialize the index for selecting time slices of the temperature data
    idx = 0
    # Define the contour levels for the temperature plot
    levels = np.linspace(6, 32, 18)

    map_prop = {'lon_step': 30,
                'lat_step': 15,
                'map_resolution': 50,
                'lw_shape': 1.5,
                'color_river': 'darkcyan',
                'fontsize_latlon': 10}

    central_longitude = 180

    # Loop through each row and column to create a grid of subplots
    for ri in range(num_rows):
        for ci in range(num_columns):
            # Add axes to the figure with the calculated properties
            ax = fig.add_axes([x_coords[ci], y_coords[ri],
                               x_fig, y_fig],
                              # projection=projection
                              )

            ax = format_hovmoller_longitude_axis(
                ax, lon_values=np.linspace(0, 360, 10), lon_extent=(0, 359),
                lon_step=120,
                central_longitude=central_longitude, tick_fontsize=10,
                show_labels=True, show_grid=False, number_format='.0f')
            # Add geographic features to the plot
            # ax = add_map_features(ax, **map_prop)

            # Set the image extent and aspect ratio of the plot
            # ax.set_extent(img_extent, projection)
            # ax.set_aspect('auto')

            # Remove y-axis labels for subplots that aren't in the first column
            if ci > 0:
                ax.set_yticklabels([])

            # Remove x-axis labels for subplots that are not in the last row
            if ri < (num_rows - 1):
                ax.set_xticklabels([])

            # Increment the index to move to the next time slice
            idx += 1
    # Geographic maps
    for ci in range(num_columns):
        ax_map = fig.add_axes([x_coords[ci], y_coords[-1], x_fig, y_map],
                              projection=ccrs.PlateCarree(
                                  central_longitude=central_longitude))

        ax_map = add_hovmoller_reference_map(
            ax_map, lat_band=(-5, 5), lat_extent=(-15, 15),
            central_longitude=central_longitude,
            lon_extent=(0, 360), lon_step=120,
            band_color='tab:purple', band_alpha=0.25,
            band_lines=True, coastlines=True, land_color='0.88',
            gridlines=True, fontsize=12, map_resolution='110m')

        if ci > 0:
            ax_map.set_yticklabels([])

    label = 'Temperature [°C]'

    grid_prop = (x_coords, y_coords, x_fig, y_fig)

    add_colorbar_col(fig, cs, label, grid_prop,
                     col_idx=[0, 1], y_coord_cbar=-0.3)
    add_colorbar_col(fig, cs, label, grid_prop,
                     col_idx=[2, 3], y_coord_cbar=-0.3)

    add_colorbar_row(fig, cs, label, grid_prop, row_idx=[0, 1])
    add_colorbar_row(fig, cs, label, grid_prop, row_idx=[2, 3])

# %%
