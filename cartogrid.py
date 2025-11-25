# %%
import cartopy.crs as ccrs
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd


def add_map_features(ax, lon_step=30, lat_step=15, map_resolution=50,
                        countries=True, coastline=True,
                        departamentos=False, subregiones=False,
                        amva=False, antioquia=False, rivers=False,
                        mpio_antioquia=False, **kwargs):
    """
    Add continents, coastlines, gridlines, and tick labels to a Cartopy axes.
    Additionally, it can add features such as countries,
    Colombian's departments,  Antioquia department, the AMVA area, and rivers.
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
    departamentos : bool, optional
        If True, adds department borders of Colombia to the axes,
        by default False.
    amva : bool, optional
        If True, adds the Metropolitan Area of the Aburrá Valley (AMVA) to
        the axes, by default False.
    antioquia : bool, optional
        If True, adds Antioquia's borders to the axes, by default False.
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

    import os
    import numpy as np
    import cartopy.crs as ccrs
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    import cartopy.feature as cfeature
    from cartopy.io.shapereader import Reader
    import geopandas as gpd

    color_shape = kwargs.get('color_shape', 'k')
    lw_shape = kwargs.get('lw_shape', 0.8)

    color_country = kwargs.get('color_country', 'k')
    lw_country = kwargs.get('lw_country', 1)

    color_mpio = kwargs.get('color_mpio', 'dimgray')
    lw_mpio = kwargs.get('lw_mpio', 0.7)

    color_river = kwargs.get('color_river', 'gray')
    lw_river = kwargs.get('lw_river', 0.6)

    fontsize_latlon = kwargs.get('fontsize_latlon', 14)
    lw_coastlines = kwargs.get('lw_coastlines', 0.8)

    lon_val = np.arange(-180, 180, lon_step)

    # Set the tick locations and labels for the axes
    ax.set_xticks(lon_val, crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-90, 91, lat_step), crs=ccrs.PlateCarree())
    ax.tick_params(axis='both', which='major', labelsize=fontsize_latlon,
                   color="#434343")
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.set_axisbelow(False)

    # Add gridlines to the axes
    ax.grid(which='major', linestyle='--', linewidth='0.6', color='gray',
            alpha=0.8, zorder=9)

    if coastline:
        # Add coastlines to the axes
        ax.coastlines(resolution=f'{map_resolution}m', color='k', alpha=1,
                    lw=lw_coastlines, zorder=10)

    if countries:
        # Load a high-resolution map of country borders
        Borders = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_0_boundary_lines_land',
            scale=f'{map_resolution}m',
            facecolor='none'
        )

        # Add country borders to the axes
        ax.add_feature(Borders, edgecolor=color_country, facecolor='None',
                       alpha=1, lw=lw_country, zorder=11)

    if departamentos:
        root = os.path.join(os.path.dirname(__file__), 'shapes/COL_shp/')
        path_shape = f'{root}gadm36_COL_1.shp'
        ax.add_geometries(Reader(path_shape).geometries(),
                          ccrs.PlateCarree(),
                          facecolor='none', edgecolor=color_shape, lw=lw_shape,
                          zorder=12)

    if amva:
        root = os.path.join(os.path.dirname(__file__), 'shapes/AMVA/')
        path_shape = f'{root}AreaMetropolitana.shp'
        ax.add_geometries(Reader(path_shape).geometries(),
                          ccrs.PlateCarree(),
                          facecolor='none', edgecolor=color_shape, lw=lw_shape,
                          zorder=13)
    if antioquia:
        root = os.path.join(os.path.dirname(__file__), 'shapes/Antioquia/')
        path_shape = f'{root}Antioquia.shp'
        ax.add_geometries(Reader(path_shape).geometries(),
                          ccrs.PlateCarree(),
                          facecolor='none', edgecolor=color_shape, lw=lw_shape,
                          zorder=12)
    if subregiones:
        root = os.path.join(os.path.dirname(__file__),
                            'shapes/Subregiones_Antioquia/')
        path_shape = f'{root}subregiones.shp'
        ax.add_geometries(Reader(path_shape).geometries(),
                          ccrs.PlateCarree(),
                          facecolor='none', edgecolor=color_shape, lw=lw_shape,
                          zorder=12)
    if mpio_antioquia:
        root = os.path.join(os.path.dirname(__file__),
                            'shapes/Municipios_Antioquia/')
        path_shape = f'{root}municipios_.shp'
        
        gdf = gpd.read_file(path_shape)
        gdf = gdf.to_crs(epsg=4326)
        ax.add_geometries(gdf.geometry,
                          ccrs.PlateCarree(),
                          facecolor='none',
                          edgecolor=color_mpio,
                          lw=lw_mpio,
                          zorder=11)
    if rivers:
        # Load a high-resolution map of river centerlines
        Rivers = cfeature.NaturalEarthFeature(
            category='physical',
            name='rivers_lake_centerlines',
            scale=f'{map_resolution}m',
            facecolor='none')

        # Add rivers to the axes
        ax.add_feature(Rivers, edgecolor=color_river, facecolor='None',
                       lw=lw_river, zorder=11)
    return ax


def define_grid_fig(num_rows, num_columns,
                    horiz_spacing=0.015, vert_spacing=0.05, **kwargs):
    """
    Calculate the coordinates and dimensions of the subplots in a grid figure.

    Parameters
    ----------
    num_rows : int
        The number of rows in the grid.
    num_columns : int
        The number of columns in the grid.
    horiz_spacing : float, optional
        The horizontal spacing between subplots, by default 0.015.
    vert_spacing : float, optional
        The vertical spacing between subplots, by default 0.05.
    **kwargs : dict, optional
        Additional keyword arguments for customizing the borders of the grid.
        These can include 'left_border', 'right_border', 'top_border',
        and 'bottom_border'. 
        If not provided, default values are 0.01 for 'left_border'
        and 'right_border' and 0.03 for 'top_border' and 'bottom_border'.

    Returns
    -------
    x_coords : list
        List of x-coordinates of the lower-left corner of each subplot.
    y_coords : list
        List of y-coordinates of the lower-left corner of each subplot.
    x_fig : float
        Width of each subplot.
    y_fig : float
        Height of each subplot.
    """

    # Set the left and right borders, and horizontal spacing between subplots
    left_border = kwargs.get('left_border', 0.01)
    right_border = kwargs.get('right_border', 0.03)
    x_corner = kwargs.get(
        'x_corner', lambda x: left_border + (x) * (x_fig + horiz_spacing))

    # Calculate the width of each subplot
    x_fig = (1 - (left_border + right_border +
             (num_columns - 1) * horiz_spacing)) / num_columns

    # Calculate the x-coordinates of the lower-left corner of each subplot
    x_coords = [x_corner(i) for i in range(num_columns)]

    # Set the top and bottom borders, and vertical spacing between subplots
    top_border = kwargs.get('top_border', 0.03)
    bottom_border = kwargs.get('bottom_border', 0.03)

    # Calculate the height of each subplot
    y_fig = (1 - (top_border + bottom_border +
             (num_rows - 1) * vert_spacing)) / num_rows

    # Calculate the y-coordinates of the lower-left corner of each subplot
    y_coords = np.flip([bottom_border + i * (y_fig + vert_spacing)
                        for i in range(num_rows)])

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


def add_colorbar_col(fig, cs, label, grid_prop, col_idx,
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

    # Calculate the axes of the colorbar for a horizontal orientation
    cbaxes = fig.add_axes([
        x_coords[col_idx] + (1-cbar_factor)*(x_fig)/2,
        y_coord_cbar,
        (x_fig)*cbar_factor,
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

    # Calculate the axes of the colorbar for a vertical orientation
    cbaxes = fig.add_axes([x_coord_cbar,
                           y_coords[row_idx] + (1-cbar_factor) *
                           (y_fig)/2,
                           cbar_width,
                           (y_fig)*cbar_factor])

    # Add a vertical colorbar to the figure
    if ticks is not None:
        cbar = fig.colorbar(cs, cax=cbaxes, label=label,
                            extend=extend, ticks=ticks)
    else:
        cbar = fig.colorbar(cs, cax=cbaxes, label=label, extend=extend)
    cbar.ax.tick_params(labelsize=fontsize)
    cbar.set_label(label, fontsize=fontsize)


if __name__ == '__main__':

    # Define the map projection (PlateCarree) and set the image extent
    proj = ccrs.PlateCarree(central_longitude=0)
    img_extent = (-77.5, -73.5, 5, 9)

    # Define the grid size (number of rows and columns)
    num_rows = 1
    num_columns = 1

    # Use the function to calculate properties of the grid
    grid_prop = x_coords, y_coords, x_fig, y_fig = define_grid_fig(
        num_rows, num_columns)

    # Define font properties for axis labels and title
    font_prop = {'fontsize': 12, 'fontweight': 'semibold', 'color': '#434343'}
    font_prop_title = {'fontsize': 14,
                       'fontweight': 'semibold', 'color': '#434343'}

    # Create a figure with a specified size
    fig = plt.figure(figsize=(7, 10))

    # Initialize the index for selecting time slices of the temperature data
    idx = 0
    # Define the contour levels for the temperature plot
    levels = np.linspace(6, 32, 18)

    map_prop = {'subregiones': True,
                'mpio_antioquia': True,
                'rivers': True,
                'lon_step': 2.5,
                'lat_step': 2.5,
                'map_resolution': 10,
                'lw_shape': 1.5,
                'color_river': 'darkcyan',}

    # Loop through each row and column to create a grid of subplots
    for fi in range(num_rows):
        for ci in range(num_columns):
            # Add axes to the figure with the calculated properties
            ax = fig.add_axes([x_coords[ci], y_coords[fi],
                               x_fig, y_fig],
                              projection=proj)
            # Add geographic features to the plot
            ax = add_map_features(ax, **map_prop)

            # Set the image extent and aspect ratio of the plot
            ax.set_extent(img_extent, proj)
            #ax.set_aspect('auto')

            # Remove y-axis labels for subplots that aren't in the first column
            if ci > 0:
                ax.set_yticklabels([])

            # Remove x-axis labels for subplots that are not in the last row
            if fi < (num_rows - 1):
                ax.set_xticklabels([])

            # Increment the index to move to the next time slice
            idx += 1
