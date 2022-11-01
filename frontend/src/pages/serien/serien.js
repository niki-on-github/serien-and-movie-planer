import React from "react";
import DataGrid, {
  Pager,
  FilterRow
} from "devextreme-react/data-grid";

const columns = ['title', 'season', 'date'];

export default function Serien() {
  return (
    <>
      <h2 className={"content-block"}>Serien</h2>

      <DataGrid
        dataSource="v1/serien"
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
