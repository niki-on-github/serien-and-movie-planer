import React from "react";
import DataGrid, {
  Pager,
  FilterRow
} from "devextreme-react/data-grid";

const columns = ['title', 'longTitle', 'date'];

export default function Movies() {
  return (
    <>
      <h2 className={"content-block"}>Movies</h2>

      <DataGrid
        dataSource="v1/movies"
        defaultColumns={columns}
        showBorders={true}
        columnAutoWidth={true}
        columnHidingEnabled={true}
      >
        <Pager showPageSizeSelector={true} showInfo={true} />
        <FilterRow visible={true} />
      </DataGrid>
    </>
  );
}
