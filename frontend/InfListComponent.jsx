import React from "react";
import { VariableSizeList as List } from "react-window";
import InfiniteLoader from "react-window-infinite-loader";

export default function InfListComponent(props) {
  // If there are more items to be loaded then add an extra row to hold a loading indicator.
  const itemCount = props.hasNextPage ? props.items.length + 1 : props.items.length;

  // Only load 1 page of items at a time.
  // Pass an empty callback to InfiniteLoader in case it asks us to load more than once.
  const loadMoreItems = props.isNextPageLoading ? () => {} : props.loadNextPage;

  // Every row is loaded except for our loading indicator row.
  const isItemLoaded = index => !props.hasNextPage || index < props.items.length;

  return (
    <InfiniteLoader
      isItemLoaded={isItemLoaded}
      itemCount={itemCount}
      loadMoreItems={loadMoreItems}
    >
      {({ onItemsRendered, ref }) => (
        <List
          className="List"
          itemCount={itemCount}
          onItemsRendered={onItemsRendered}
          ref={ref}
          height={500}
          itemSize={() => 50}
        >
          {props.children}
        </List>
      )}
    </InfiniteLoader>
  );
}
