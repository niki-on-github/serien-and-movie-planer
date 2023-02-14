import React from "react";
import DataGrid, {
  Pager,
  Column,
  Editing,
  FilterRow,
  Lookup,
} from "devextreme-react/data-grid";
import { createStore } from 'devextreme-aspnet-data-nojquery';
import { states } from '../../data/states'
import Box from "@mui/material/Box";


const store = createStore({
    key: "id",
    loadUrl: "/api/v1/serien",
    insertUrl: "/api/v1/serien/insert",
    updateUrl: "/api/v1/serien/update",
    deleteUrl: "/api/v1/serien/delete"
});

export default function Serien() {
  return (
    <Box sx={{ m: 2 }}>
      <DataGrid
        dataSource={store}
        showBorders={true}
        columnAutoWidth={true}
        columnHidingEnabled={true}
      >
        <Pager showPageSizeSelector={true} showInfo={true} />
        <FilterRow visible={true} />
        <Editing
          mode="cell"
          allowUpdating={true}
          allowAdding={false}
          allowDeleting={false}
        />

        <Column dataField="title" caption="Title" dataType="string"/>
        <Column dataField="season" caption="Season" dataType="number"/>
        <Column dataField="date" caption="Date" dataType="date"/>
        <Column dataField="state" caption="State" dataType="string" filterValue="New">
          <Lookup dataSource={states} valueExpr="ID" displayExpr="Name" />
        </Column>
      </DataGrid>
    </Box>
  );
}
